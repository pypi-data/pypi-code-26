import torch.nn as nn

class Generator(nn.Module):
    def __init__(self):
        super(Generator, self).__init__()

        preprocess = nn.Sequential(
            nn.Linear(128, 4*4*4*DIM),
            nn.ReLU(True),
        )
        block1 = nn.Sequential(
            nn.ConvTranspose2d(4*DIM, 2*DIM, 5),
            nn.ReLU(True),
        )
        block2 = nn.Sequential(
            nn.ConvTranspose2d(2*DIM, DIM, 5),
            nn.ReLU(True),
        )
        deconv_out = nn.ConvTranspose2d(DIM, 1, 8, stride=2)

        self.block1 = block1
        self.block2 = block2
        self.deconv_out = deconv_out
        self.preprocess = preprocess
        self.sigmoid = nn.Sigmoid()

    def forward(self, input):
        output = self.preprocess(input)
        output = output.view(-1, 4*DIM, 4, 4)
        output = self.block1(output)
        output = output[:, :, :7, :7]
        output = self.block2(output)
        output = self.deconv_out(output)
        output = self.sigmoid(output)
        return output.view(-1, OUTPUT_DIM)

class Discriminator(nn.Module):
    def __init__(self):
        super(Discriminator, self).__init__()

        main = nn.Sequential(
            nn.Conv2d(1, DIM, 5, stride=2, padding=2),
            nn.ReLU(True),
            nn.Conv2d(DIM, 2*DIM, 5, stride=2, padding=2),
            nn.ReLU(True),
            nn.Conv2d(2*DIM, 4*DIM, 5, stride=2, padding=2),
            nn.ReLU(True),
        )
        self.main = main
        self.output = nn.Linear(4*4*4*DIM, 1)

    def forward(self, input):
        input = input.view(-1, 1, 28, 28)
        out = self.main(input)
        out = out.view(-1, 4*4*4*DIM)
        out = self.output(out)
        return out.view(-1)


class ResBlock(nn.Module):
    def __init__(self, dim):
        super(ResBlock, self).__init__()
        self.res_block = nn.Sequential(
            nn.ReLU(True),
            nn.Conv1d(dim, dim, 5, padding=2),  # nn.Linear(DIM, DIM),
            nn.ReLU(True),
            nn.Conv1d(dim, dim, 5, padding=2),  # nn.Linear(DIM, DIM),
        )

    def forward(self, input):
        output = self.res_block(input)
        return input + (0.3 * output)


class Generator(nn.Module):
    def __init__(self, dim, seq_len, vocab_size):
        super(Generator, self).__init__()
        self.dim = dim
        self.seq_len = seq_len

        self.fc1 = nn.Linear(128, dim * seq_len)
        self.block = nn.Sequential(
            ResBlock(dim),
            ResBlock(dim),
            ResBlock(dim),
            ResBlock(dim),
            ResBlock(dim),
        )
        self.conv1 = nn.Conv1d(dim, vocab_size, 1)
        self.softmax = nn.Softmax()

    def forward(self, noise):
        batch_size = noise.size(0)
        output = self.fc1(noise)
        # (BATCH_SIZE, DIM, SEQ_LEN)
        output = output.view(-1, self.dim, self.seq_len)
        output = self.block(output)
        output = self.conv1(output)
        output = output.transpose(1, 2)
        shape = output.size()
        output = output.contiguous()
        output = output.view(batch_size * self.seq_len, -1)
        output = self.softmax(output)
        # (BATCH_SIZE, SEQ_LEN, len(charmap))
        return output.view(shape)


class Discriminator(nn.Module):
    def __init__(self, dim, seq_len, vocab_size):
        super(Discriminator, self).__init__()
        self.dim = dim
        self.seq_len = seq_len

        self.block = nn.Sequential(
            ResBlock(dim),
            ResBlock(dim),
            ResBlock(dim),
            ResBlock(dim),
            ResBlock(dim),
        )
        self.conv1d = nn.Conv1d(vocab_size, dim, 1)
        self.linear = nn.Linear(seq_len * dim, 1)

    def forward(self, input):
        # (BATCH_SIZE, VOCAB_SIZE, SEQ_LEN)
        output = input.transpose(1, 2)
        output = self.conv1d(output)
        output = self.block(output)
        output = output.view(-1, self.seq_len * self.dim)
        output = self.linear(output)
        return output
