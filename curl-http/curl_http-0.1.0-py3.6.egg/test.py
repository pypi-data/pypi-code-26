from httplib import HTTP

http = HTTP()
#http.set_cookie("name","luoliang")
http.set_header("Content","dffdf")
#print(http.request("http://hello_flask.it592.com/cookie/",{"name":123,"value":456}))
#(http.request("http://hello_flask.it592.com/cookie/"))
(http.request("http://jwgl2.ouc.edu.cn/cas/login.action",{"name":123,"value":456}))
print(http.cookie_list)
(http.request("http://jwgl2.ouc.edu.cn/cas/login.action",{"name":123,"value":456}))
print(http.cookie_list)
print(http.get_header())
print(http.response_code)
print(http.request("http://hello_flask.it592.com/headers/"))
http.set_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36")
print(http.request("http://hello_flask.it592.com/headers/"))
http.set_proxy("114.212.12.4","31228") #代理测试成功
#print(http.request("http://myip.kkcha.com/"))
http.set_timeout(1)#超时检测成功
print(http.request("http://myip.kkcha.com/"))