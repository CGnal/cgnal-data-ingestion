import smtplib
from typing import List
from os.path import basename

from cgnal.logging.defaults import WithLogging

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


class EmailSender(WithLogging):
    """
        Email Sender Utility Class

        ...

        Attributes
        ----------
        email_address : str
            Email Address of the sender
        username : str
            Username for login
        password : str
            Password for login
        smtp_address : str
            SMTP address of the SMTP server
        auth_protocol : str
            STMP Authentication protocol can be "TSL" or "SSL"
        port: int
            Port for SMTP server

        Methods
        -------
        send_mail(text, destination)
            Send the mail with a specific text to a specific destination
        """

    def __init__(self, email_address: str, username: str, password: str, smtp_address: str, auth_protocol: str = "None",
                 port: int = None):
        """
            :param email_address: Sender email address
            :type email_address: str
            :param username: Username for authentication
            :type username: str
            :param password: Password for authentication
            :type password: str
            :param smtp_address: SMTP server address
            :type smtp_address: str
            :param auth_protocol: Authentication protocol to use
            :type auth_protocol: str
            :param port: Port of SMTP server
            :type port: int
        """
        self.email_address = email_address
        self.username = username
        self.password = password
        self.smtp_address = smtp_address
        self.auth_protocol = auth_protocol
        self.port = port

    def send_mail(self, text: str, subject: str, destination: str, attachments: List[str] = None):
        """
        :param text: The text of the email
        :type text: str
        :param subject: The subject of the email
        :type subject: str
        :param destination: The destination email address
        :type destination: str
        :param attachments: List with the files to send as attachments to the email
        :type attachments: List[str]
        :return:
        """

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = self.email_address
        msg['To'] = destination
        msg.attach(MIMEText(text))
        if attachments is not None:
            for f in attachments:
                with open(f, "rb") as fil:
                    part = MIMEApplication(
                        fil.read(),
                        Name=basename(f)
                    )
                # After the file is closed
                part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
                msg.attach(part)

        try:
            if self.auth_protocol == "SSL":
                port = 465 if self.port is None else self.port
                server = smtplib.SMTP_SSL(self.smtp_address, port=port)
            elif self.auth_protocol == "TLS":
                port = 587 if self.port is None else self.port
                server = smtplib.SMTP(self.smtp_address, port=port)
                server.starttls()
            elif self.auth_protocol == "None":
                port = 25 if self.port is None else self.port
                server = smtplib.SMTP(self.smtp_address, port=port)
            else:
                raise Exception(f"{self.auth_protocol} not implemented")
            server.ehlo()
            server.login(self.username, self.password)
            server.sendmail(self.email_address, destination, msg.as_string())
            server.close()
        except Exception as e:
            raise e
