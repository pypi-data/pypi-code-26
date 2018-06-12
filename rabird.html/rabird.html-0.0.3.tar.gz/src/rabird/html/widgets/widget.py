class LxmlElementWrapper(object):
    def __init__(self, element):
        self._element = element

    def xpath(self, pattern):
        return self._element.xpath(pattern)

    def get_attribute(self, name, default=None):
        return self._element.attrib.get(name, default)

class RabirdSeleniumElementWrapper(object):
    def __init__(self, element):
        self._element = element

    def xpath(self, pattern):
        return self._element.xpath_find_all(pattern)

    def get_attribute(self, name, default=None):
        attribute = self._element.get_attribute(name)
        if attribute is None:
            return default

        return attribute

class ElementTreeElementWrapper(object):
    def __init__(self, element):
        self._element = element

    def xpath(self, pattern):
        return self._element.findall(pattern)

    def get_attribute(self, name, default=None):
        return self._element.attrib.get(name, default)

class SeleniumElementWrapper(object):
    def __init__(self, element):
        self._element = element

    def xpath(self, pattern):
        return self._element.find_elements_by_xpath(pattern)

    def get_attribute(self, name, default=None):
        attribute = self._element.get_attribute(name)
        if attribute is None:
            return default

        return attribute

def createElementWrapper(element):
    if hasattr(element, "xpath"):
        # Support lxml elements
        return LxmlElementWrapper(element)
    elif hasattr(element, "xpath_find_all"):
        # Support rabird.selenium elements
        return RabirdSeleniumElementWrapper(element)
    elif hasattr(element, "findall"):
        # Support python ElementTree elements
        return ElementTreeElementWrapper(element)
    elif hasattr(element, "find_elements_by_xpath"):
        # Support selenium elements
        return SeleniumElementWrapper(element)
    else:
        raise NotImplementedError("Unsupported element type!")

class Widget(object):
    def __init__(self, element):
        self._wrapper = createElementWrapper(element)

    @property
    def element(self):
        return self._wrapper._element
