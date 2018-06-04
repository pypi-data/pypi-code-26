import torch.nn as nn
import torch.utils.model_zoo as model_zoo


__all__ = ['AE', 'ae']


model_urls = {
    'ae': 'TODO',
}


class Autoencoder(nn.Module):
    """ Autoencoder used for adversarial transformation networks attack.

    """
    def __init__(self, encoder=None, decoder=None):
        super(Autoencoder, self).__init__()
        if encoder is None:
            self.encoder = nn.Sequential(
                nn.Conv2d(1, 16, 3, stride=3, padding=1),  # b,16,10,10
                nn.ReLU(True),
                nn.MaxPool2d(2, stride=2),  # b,16,5,5
                nn.Conv2d(16, 8, 3, stride=2, padding=1),  # b,8,3,3
                nn.ReLU(True),
                nn.MaxPool2d(2, stride=1)  # b,8,2,2
            )
        if decoder is None:
            self.decoder = nn.Sequential(
                nn.ConvTranspose2d(8, 16, 3, stride=2),  # b,16,5,5
                nn.ReLU(True),
                nn.ConvTranspose2d(16, 8, 5, stride=3, padding=1),  # b,8,15,15
                nn.ReLU(True),
                nn.ConvTranspose2d(8, 1, 2, stride=2, padding=1),  # b,1,28,28
                nn.Tanh()
            )

    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        return x


def autoencoder(pretrained=False, **kwargs):
    r"""Adversarial Transformation Networks

    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
    """
    model = AE(**kwargs)
    if pretrained:
        model.load_state_dict(model_zoo.load_url(model_urls['ae']))
    return model
