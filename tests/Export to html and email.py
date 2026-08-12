# region: Docstring
'''
Author: Wim Gielis (wim.gielis@gmail.com)
Timing: January 2025
'''
# endregion

# region: Imports
import os
import re
import uuid
from datetime import datetime
from pykeepass import PyKeePass
from jinja2 import Template

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
# endregion

# region: Constant values
KEEPASS_DB_PATH = "D:/Paswoorden.kdbx"
KEEPASS_DB_PASSWORD = "test"
OUTPUT_HTML_FILE = "D:/pw.html"
HTML_TEMPLATE_FILE = "D:/template_for_export.html"

DATE_FORMAT = '%d-%m-%Y'

# For sending the HTML file by email
SEND_EMAIL = True
RECIPIENT_EMAIL = "your_email_address@gmail.com"
SENDER_EMAIL = "your_email_address@gmail.com"
SENDER_PASSWORD = "your_Google_app_password"
EMAIL_SUBJECT = f"pw ({datetime.now().strftime(DATE_FORMAT)})"
EMAIL_BODY = "" # "Please find attached the KeePass export file."
# endregion

# region: Main code
def write_to_file(full_file_name, file_contents):
    with open(full_file_name, "w", encoding="utf-8") as f:
        f.write(file_contents)

def format_date(date_obj):
    """
    Format a datetime object as 'dd-mm-yyyy'.
    If the date_obj is None, return 'N/A'.
    """
    return date_obj.strftime(DATE_FORMAT) if date_obj else 'N/A'

def send_email(file_path, recipient_email, sender_email, sender_password, email_subject, email_body):
    """
    Send an email with the generated HTML file as an attachment.
    
    :param file_path: Path to the HTML file to attach.
    :param recipient_email: Recipient's email address.
    :param sender_email: Sender's Gmail address.
    :param sender_password: Sender's Gmail app password.
    """

    # Create a new email
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = email_subject
    message.attach(MIMEText(email_body, 'plain'))

    # Attach the HTML file
    with open(file_path, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
        message.attach(part)

    # Send the email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)

    print(f"Email sent successfully to {recipient_email}")

def export_keepass_to_html(db_path, password, output_file, template_file):

    try:
        # Load the KeePass database
        kp = PyKeePass(db_path, password=password)

        def resolve_username(entry):
            '''
            Function to derive the username for an entry
            '''
            if isinstance(entry.username, str):
                if re.match(r'^\{REF:U.*:[0-9A-Z]{32}\}', entry.username):
                    return entry.deref('username')
                else:
                    return entry.username
            elif entry.username is not None:
                referenced_entry = kp.find_entries(uuid=entry.username, first=True)
                return referenced_entry.username if referenced_entry else "Unresolved Reference"
            return "No Username"

        def resolve_password(entry):
            '''
            Function to derive the password for an entry
            '''
            if isinstance(entry.password, str):
                if re.match(r'^\{REF:P.*:[0-9A-Z]{32}\}', entry.password):
                    return entry.deref('password')
                else:
                    return entry.password
            elif entry.password is not None:
                referenced_entry = kp.find_entries(uuid=entry.password, first=True)
                return referenced_entry.password if referenced_entry else "Unresolved Reference"
            return "No Password"

        def extract_group_iterative(root_groups):
            '''
            Iterative function to extract groups and their subgroups
            '''
            stack = [{"group": group, "parent_id": None} for group in root_groups]
            group_data = []

            while stack:
                current = stack.pop()
                group = current["group"]
                parent_id = current["parent_id"]

                group_info = {
                    "id": f"group-{uuid.uuid4().hex}",
                    "name": group.name,
                    "parent_id": parent_id,
                    "entries": sorted([
                        {
                            "title": entry.title or "No Title",
                            "username": resolve_username(entry) or "No Username",
                            "password": resolve_password(entry) or "No Password",
                            "url": entry.url or "No URL",
                            "notes": (entry.notes or "No Notes").replace("\n", "<br>"),
                            "custom_properties": entry.custom_properties or {},
                            "ctime": format_date(entry.ctime),
                            "mtime": format_date(entry.mtime),
                            "expiry_time": format_date(entry.expiry_time),
                            "expired": entry.expired
                        }
                        for entry in group.entries], key=lambda e: e["title"].lower())
                }

                # Add the current group's subgroups to the stack for processing
                stack.extend( sorted(
                        [{"group": subgroup, "parent_id": group_info["id"]} for subgroup in group.subgroups],
                        key=lambda sg: sg["group"].name.lower()
                    ))
                group_data.append(group_info)

            # Sort all groups by their name (case insensitive)
            return sorted(group_data, key=lambda g: g["name"].lower())

        # Extract all groups iteratively
        root_groups = [group for group in kp.groups if group.group is None]
        grouped_entries = extract_group_iterative(root_groups)

        # Load the HTML template
        with open(template_file, "r", encoding="utf-8") as template_file_obj:
            template_content = template_file_obj.read()
            template = Template(template_content)

        # Render the HTML and write to a file
        html_output = template.render(grouped_entries=grouped_entries)
        write_to_file(output_file, html_output)

        print(f"Export completed. HTML saved to: {output_file}")

    except Exception as e:
        print(f"Error occurred: {e}")
# endregion

# region: Call the script
if __name__ == "__main__":

    example_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KeePass export</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { text-align: center; }
        .group, .subgroup { margin-left: 20px; }
        .entry { margin-bottom: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; position: relative; }
        .entry-title { font-size: 1.2em; font-weight: bold; }
        .entry-field { margin: 5px 0; }
        .entry-field span { font-weight: bold; }
        .custom-properties-bullet span { font-weight: bold; }
        .expired-icon { color: red; margin-right: 5px; }
        .up-link { position: absolute; top: 10px; right: 10px; text-decoration: none; font-size: 0.9em; color: blue; }
        .up-link:hover { text-decoration: underline; }
        .toc { margin-bottom: 30px; }
        .toc ul { list-style-type: none; padding: 0; }
        .toc ul ul { margin-left: 20px; }
        .toc li { margin: 5px 0; }
    </style>
</head>
<body>
    <div class="toc">
        <h1>Table of Contents</h1>
        <ul>
            {% for group in grouped_entries %}
                {% if not group.parent_id %}
                    <li><a href="#{{ group.id }}">{{ group.name }}</a></li>
                    <ul>
                        {% for subgroup in grouped_entries %}
                            {% if subgroup.parent_id == group.id %}
                                <li><a href="#{{ subgroup.id }}">{{ subgroup.name }}</a></li>
                                <ul>
                                    {% for subsubgroup in grouped_entries %}
                                        {% if subsubgroup.parent_id == subgroup.id %}
                                            <li><a href="#{{ subsubgroup.id }}">{{ subsubgroup.name }}</a></li>
                                        {% endif %}
                                    {% endfor %}
                                </ul>
                            {% endif %}
                        {% endfor %}
                    </ul>
                {% endif %}
            {% endfor %}
        </ul>
    </div>

    <div id="groups">
        {% for group in grouped_entries %}
            {% if not group.parent_id %}
                <div class="group">
                    <h1>
                        <a id="{{ group.id }}">{{ group.name }}</a>
                    </h1>
                    <div>
                        {% for entry in group.entries %}
                            <div class="entry">
                                <div class="entry-title">
                                    {% if entry.expired %}
                                        <span class="expired-icon">❌</span>
                                    {% endif %}
                                    {{ entry.title }}
                                </div>
                                <div class="entry-field"><span>Username:</span> {{ entry.username }}</div>
                                <div class="entry-field"><span>Password:</span> {{ entry.password }}</div>
                                <div class="entry-field"><span>URL:</span> <a href="{{ entry.url }}">{{ entry.url }}</a></div>
                                <div class="entry-field"><span>Notes:</span><br> {{ entry.notes }}</div>
                                {% if entry.custom_properties %}
                                    <div class="custom-properties">
                                        <div class="custom-properties-bullet"><span>Custom properties:</span></div>
                                        {% for key, value in entry.custom_properties.items() %}
                                            <div class="custom-property"><span> - {{ key }}:</span> {{ value }}</div>
                                        {% endfor %}
                                    </div>
                                {% endif %}
                                <div class="entry-field"><span>Created:</span> {{ entry.ctime }}</div>
                                <div class="entry-field"><span>Modified:</span> {{ entry.mtime }}</div>
                                <div class="entry-field"><span>Expires:</span> {{ entry.expiry_time }}</div>
                                <a class="up-link" href="#top">⬆ Up</a>
                            </div>
                        {% endfor %}
                        {% for subgroup in grouped_entries %}
                            {% if subgroup.parent_id == group.id %}
                                <div class="subgroup">
                                    <h2>
                                        <a id="{{ subgroup.id }}">{{ subgroup.name }}</a>
                                    </h2>
                                    <div>
                                        {% for entry in subgroup.entries %}
                                            <div class="entry">
                                                <div class="entry-title">
                                                    {% if entry.expired %}
                                                        <span class="expired-icon">❌</span>
                                                    {% endif %}
                                                    {{ entry.title }}
                                                </div>
                                                <div class="entry-field"><span>Username:</span> {{ entry.username }}</div>
                                                <div class="entry-field"><span>Password:</span> {{ entry.password }}</div>
                                                <div class="entry-field"><span>URL:</span> <a href="{{ entry.url }}">{{ entry.url }}</a></div>
                                                <div class="entry-field"><span>Notes:</span><br> {{ entry.notes }}</div>
                                                {% if entry.custom_properties %}
                                                    <div class="custom-properties">
                                                        <div class="custom-properties-bullet"><span>Custom properties:</span></div>
                                                        {% for key, value in entry.custom_properties.items() %}
                                                            <div class="custom-property"><span> - {{ key }}:</span> {{ value }}</div>
                                                        {% endfor %}
                                                    </div>
                                                {% endif %}
                                                <div class="entry-field"><span>Created:</span> {{ entry.ctime }}</div>
                                                <div class="entry-field"><span>Modified:</span> {{ entry.mtime }}</div>
                                                <div class="entry-field"><span>Expires:</span> {{ entry.expiry_time }}</div>
                                                <a class="up-link" href="#top">⬆ Up</a>
                                            </div>
                                        {% endfor %}
                                        {% for subsubgroup in grouped_entries %}
                                            {% if subsubgroup.parent_id == subgroup.id %}
                                                <div class="subgroup">
                                                    <h3>
                                                        <a id="{{ subsubgroup.id }}">{{ subsubgroup.name }}</a>
                                                    </h3>
                                                    <div>
                                                        {% for entry in subsubgroup.entries %}
                                                            <div class="entry">
                                                                <div class="entry-title">
                                                                    {% if entry.expired %}
                                                                        <span class="expired-icon">❌</span>
                                                                    {% endif %}
                                                                    {{ entry.title }}
                                                                </div>
                                                                <div class="entry-field"><span>Username:</span> {{ entry.username }}</div>
                                                                <div class="entry-field"><span>Password:</span> {{ entry.password }}</div>
                                                                <div class="entry-field"><span>URL:</span> <a href="{{ entry.url }}">{{ entry.url }}</a></div>
                                                                <div class="entry-field"><span>Notes:</span><br> {{ entry.notes }}</div>
                                                                {% if entry.custom_properties %}
                                                                    <div class="custom-properties">
                                                                        <div class="custom-properties-bullet"><span>Custom properties:</span></div>
                                                                        {% for key, value in entry.custom_properties.items() %}
                                                                            <div class="custom-property"><span> - {{ key }}:</span> {{ value }}</div>
                                                                        {% endfor %}
                                                                    </div>
                                                                {% endif %}
                                                                <div class="entry-field"><span>Created:</span> {{ entry.ctime }}</div>
                                                                <div class="entry-field"><span>Modified:</span> {{ entry.mtime }}</div>
                                                                <div class="entry-field"><span>Expires:</span> {{ entry.expiry_time }}</div>
                                                                <a class="up-link" href="#top">⬆ Up</a>
                                                            </div>
                                                        {% endfor %}
                                                    </div>
                                                </div>
                                            {% endif %}
                                        {% endfor %}
                                    </div>
                                </div>
                            {% endif %}
                        {% endfor %}
                    </div>
                </div>
            {% endif %}
        {% endfor %}
    </div>
</body>
</html>
    """

    if not os.path.exists(HTML_TEMPLATE_FILE):
        write_to_file(HTML_TEMPLATE_FILE, example_template)

    export_keepass_to_html(KEEPASS_DB_PATH, KEEPASS_DB_PASSWORD, OUTPUT_HTML_FILE, HTML_TEMPLATE_FILE)
    if SEND_EMAIL:
        send_email(OUTPUT_HTML_FILE, RECIPIENT_EMAIL, SENDER_EMAIL, SENDER_PASSWORD, EMAIL_SUBJECT, EMAIL_BODY)
# endregion