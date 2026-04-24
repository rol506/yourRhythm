import smtplib, os, logging, sys
from dotenv import load_dotenv
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader, select_autoescape

load_dotenv()

class EmailSender:
    def __init__(self):
        self.__pass = os.environ.get("GOOGLE_APP_PASS")
        self.__addr = os.environ.get("GOOGLE_MAIL")
        self.__env = Environment(loader=FileSystemLoader('./templates/'), autoescape=select_autoescape(['html']))
    
    def sendHTML(self, html: str, subject: str, addr: str):
        msg = EmailMessage()

        msg['Subject'] = subject
        msg['From'] = self.__addr
        msg['To'] = addr
        msg.set_content(html, subtype="html")

        #part1 = MIMEText(alt, "plain")
        #part2 = MIMEText(html, "html")

        #msg.attach(part1)
        #msg.attach(part2)

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(self.__addr, self.__pass)
            server.send_message(msg)

    def sendTaskReminder(self, tasks: list[str], addrs: list[str]):
        if (len(tasks) == 0):
            return;
        msg = EmailMessage()
        msg["Subject"] = "У вас остались невыполненные задания"
        msg['From'] = self.__addr
        msg['To'] = ', '.join(addrs)
        header = "Срок на выполнение ваших задач подходит к концу! Пора их выполнить!"
        msg.set_content(self.__env.get_template("emailBase.html").render(tasks=tasks, header=header), subtype="html")

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(self.__addr, self.__pass)
            server.send_message(msg)

    def sendHometaskReminder(self, tasks: list[str], addrs: list[str], customHeader=None):
        if (len(tasks) == 0):
            return;
        msg = EmailMessage()
        msg["Subject"] = "У вас остались невыполненные домашние задания"
        msg['From'] = self.__addr
        msg['To'] = ', '.join(addrs)
        header = "У вас остались невыполненные домашние задания! Пора приступать к выполнению!" if customHeader is None else customHeader
        msg.set_content(self.__env.get_template("emailBase.html").render(tasks=tasks, header=header), subtype="html")

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(self.__addr, self.__pass)
            server.send_message(msg)
