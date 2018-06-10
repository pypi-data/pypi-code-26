from browser import document

document.bind('click', ".RDNT-ignore_link", lambda evt: evt.preventDefault())
