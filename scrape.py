from selenium import webdriver
from datetime import datetime
from twilio.rest import Client
from decouple import config
from playsound import playsound
import time
import sched


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


# twilio config
account_sid = config("ACCOUNT_SID")
auth_token = config("AUTH_TOKEN")
client = Client(account_sid, auth_token)

my_url = "https://app.beefy.finance/"
browser = webdriver.Chrome(
    executable_path=("J:\dev-tools\ChromeDriver\chromedriver.exe")
)
browser.get(my_url)

# Creating an instance of the
# scheduler class
scheduler = sched.scheduler(time.time, time.sleep)


def send_sms():
    content = "Alert from PY web crawler at: " + str(datetime.now())
    message = client.messages.create(
        body=content, from_=config("TWILIO_PHONE"), to=config("MY_PHONE")
    )
    print(message.sid)


# refresh webpage and notify me if anything has changed in the last 5 mins
def check_tokens(cached_tokens):

    # refreshing
    browser.refresh()

    # "p.MuiTypography-root.MuiTypography-body2.MuiTypography-gutterBottom"
    token_containers = browser.find_elements_by_css_selector(
        "div.MuiGrid-root.MuiGrid-item.MuiGrid-grid-xs-3"
    )

    token_names = map(
        lambda container: container.find_element_by_css_selector(
            "p.MuiTypography-root.MuiTypography-body2.MuiTypography-gutterBottom"
        ).text,
        token_containers,
    )

    retrieved_tokens = set(token_names)

    print("Tick at: ", datetime.now())
    if cached_tokens != retrieved_tokens:
        print(bcolors.OKGREEN + "------ Alert! -------- " + bcolors.ENDC)
        print(bcolors.OKGREEN + "new tokens: " + str(retrieved_tokens) + bcolors.ENDC)
        cached_tokens = retrieved_tokens
        # send_sms()
        playsound("crow-sound.mp3")

    scheduler.enter(60, 1, check_tokens, (cached_tokens,))


cached_tokens = set()

# enter(delay in seconds, task Priority, function to be called, tupleOfParameters to be provided to function)
scheduler.enter(2, 1, check_tokens, (cached_tokens,))
scheduler.run()
