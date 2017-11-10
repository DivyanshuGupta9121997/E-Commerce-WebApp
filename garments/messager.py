import cookielib
from getpass import getpass
import urllib2

# modify accordingly
# proxy = urllib2.ProxyHandler({'http': 'http://USERNAME:PASSWORD@10.1.1.45:80'})
# auth = urllib2.HTTPBasicAuthHandler()
cj= cookielib.CookieJar()
# opener = urllib2.build_opener(proxy,auth,urllib2.HTTPHandler,urllib2.HTTPCookieProcessor(cj))
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
def sendSMS(number,message,username,passwd):
    global opener
    message = "+".join(message.split(' '))
    message+="+"*(140-len(message))
    #print len(message)

 #logging into the sms site
    url ='http://site24.way2sms.com/Login1.action?'
    data = 'username='+username+'&password='+passwd+'&Submit=Sign+in'   

 #Adding header details
    opener.addheaders=[('User-Agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120')]
    try:
        usock =opener.open(url, data)
    except IOError:
        # print "Error while sending sms"
        return False
        #print "error"
        #return()

    jession_id =str(cj).split('~')[1].split(' ')[0]
    send_sms_url = 'http://site24.way2sms.com/smstoss.action?'
    send_sms_data = 'ssaction=ss&Token='+jession_id+'&mobile='+number+'&message='+message+'&msgLen=136'
    opener.addheaders=[('Referer', 'http://site25.way2sms.com/sendSMS?Token='+jession_id)]
    try:
        sms_sent_page = opener.open(send_sms_url,send_sms_data)
    except IOError:
        # print "Error while sending SMS"
        return False
    # print 'sent message'
    return True


if __name__ == '__main__':
    sendSMS('8887802358','This is a test Message','7726029635','dhakad17')


