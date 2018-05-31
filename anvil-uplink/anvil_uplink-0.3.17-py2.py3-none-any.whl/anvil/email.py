import anvil.server


#!defClass(anvil.email,SendFailure)!:
class SendFailure(anvil.server.AnvilWrappedError):
    pass

anvil.server._register_exception_type("anvil.email.SendFailure", SendFailure)


#!defFunction(anvil.email,_,[to=],[cc=],[bcc=],[from_address="no-reply"],[from_name=],[subject=],[text=],[html=],[attachments=])!2: "Send an email" ["send"]
def send(**kw):
    anvil.server.call("anvil.private.email.send", **kw)

def handle_message(fn):
    return anvil.server.callable("email:handle_message")(lambda msg_dict: fn(Message(msg_dict)))

class Message(object):
    #!defAttr()!1: {name:"from_address",type:"string",description:"The email address from which this message was sent, according to the SMTP envelope."}
    #!defAttr()!1: {name:"recipient",type:"string",description:"The email address that received this message.\n\nNote that this email address may not appear in any of the headers (eg if the email has been BCCed or blind forwarded)."}
    class Envelope:
        def __init__(self, envelope):
            self.from_address = envelope['from']
            self.recipient = envelope['recipient']
    #!defClass(anvil.email..Message,Envelope)!:


    #!defAttr()!1: {name:"envelope",pyType:"anvil.email..Message.Envelope instance",description:"The sender and receipient of this email, according to the SMTP envelope."}
    #!defAttr()!1: {name:"headers",type:"list",description:"All the headers in this email, as a list of (name,value) pairs."}
    #!defAttr()!1: {name:"text",type:"string",description:"The plain-text content of this email, or None if there is no plain-text part."}
    #!defAttr()!1: {name:"subject",type:"string",description:"The subject of this email, or None if there is no subject."}
    #!defAttr()!1: {name:"html",type:"string",description:"The HTML content of this email, or None if there is no HTML part."}
    #!defAttr()!1: {name:"attachments",pyType:"list(anvil.Media instance)",description:"A list of this email's attachments"}

    def __init__(self, msg_dict):
        self.envelope = Message.Envelope(msg_dict['envelope'])
        self.headers = msg_dict['headers']
        self.subject = msg_dict['subject']
        self.text = msg_dict['text']
        self.html = msg_dict['html']
        self.attachments = msg_dict['attachments']

    #!defMethod(_,header_name)!2: "Return the value of the specified header, or None if it is not present.\n\nCase-insensitive. If the header is specified multiple times, returns the first value." ["get_header"]
    def get_header(self, header_name):
        header_name = header_name.lower()
        for name,value in self.headers:
            if name.lower() == header_name:
                return value
        return None

    #!defMethod(_,header_name)!2: "Return a list containing every value of the specified header. Case-insensitive." ["list_header"]
    def list_header(self, header_name):
        header_name = header_name.lower()
        return [value for name,value in self.headers
                if name.lower() == header_name]

    #!defMethod(_,[cc=],[bcc=],[from_address=],[from_name=],[text=],[html=],[attachments=])!2: "Reply to this email." ["reply"]
    def reply(self,**kw):
        kw['to'] = kw.get('to', self.get_header("Reply-To") or self.envelope.from_address)
        kw['subject'] = kw.get('subject', self.subject)
        kw['in_reply_to'] = self.get_header("Message-ID")
        kw['references'] = (self.get_header("References") or "") + " " + kw['in_reply_to']
        kw['from_address'] = kw.get('from_address', self.envelope.recipient)
        send(**kw)

    #!defClass(anvil.email.,Message)!:

