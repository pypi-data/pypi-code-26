from backend_template import backend_template

from flask import send_file
import os

class images_template(backend_template):



    #############################################
    #             Module methods                #
    #############################################
    def get(self, id, queries):
        try:
            return send_file(os.getcwd() + "/images/" + id + ".png", mimetype='image/png'), 200
        except:
            return "El fichero no existe o todavia no esta listo", 404



    def create(self, queries, data):
        # Get id from parent
        id = super(images_template, self).create(queries, data)

        # Start the image
        self.create_image(id, queries, data)

        return id, 201



    def create_image(self, id, queries, data):
        # pyplot.savefig('images' + id + '.png', dpi=300)
        pass


