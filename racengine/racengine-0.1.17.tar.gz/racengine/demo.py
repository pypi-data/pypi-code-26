import json
import sys
from racengine.main import Process

if __name__ == "__main__":
    file_path = sys.argv[1]
    json_path = sys.argv[2]
    renderer_endpoint = ""
    conv_endpoint = ""
    smtp_conf = "./conf.json"  # or dict {"host": "", "port": 465, "username": "", "password": ""}

    msg = {
        'to': "s.regragui@sfereno.com",
        'from': "azer@exemple.com",
        'subject': "testaze",
        'body_text': "Hi!\nHow are you?\nHere is the link you wanted:\nhttps://www.python.org",
        'body_html': """\
                            <html>
                              <head></head>
                              <body>
                                <p>Hi!<br>
                                   How are you?<br>
                                   Here is the <a href="https://www.python.org">link</a> you wanted.
                                </p>
                              </body>
                            </html>
                        """
    }

    gen_and_conv = Process(templater_endpoint=renderer_endpoint, converter_endpoint=conv_endpoint, smtp_conf=smtp_conf)

    with open(json_path, 'r', encoding='utf-8') as f:
        json_ = json.loads(json.dumps(f.read()))
        data = json_

    with open(file_path, 'rb') as f:
        template = f.read()

    gen_and_conv.run(
        flags="RCE",
        from_addr="",
        to_addr="s.regragui@sfereno.com",
        subject="Rapport de diagnostic",
        text_body="Voici votre rapport.",
        html_body="<h1>Voici votre rapport.</h1>",
        template=template, data=data
    )

    print('Finish')
