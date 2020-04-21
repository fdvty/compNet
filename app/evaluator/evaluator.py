import torch
import torch.nn.functional as F
import torch.distributions as dist

features = [
    ('gender', int, 2),
    ('age', float, 1),
    ('contact_history', int, 2),
    ('acid_test', int, 2),
    ('x_ray', int, 2),
    ('wbc', float, 1),
    ('rbc', float, 1),
    ('hgb', float, 1),
]

def read_data():
    data = {}
    for field, tp, size in features:
        while True:
            print('{}: '.format(field), end='')
            try:
                val = float(input())
            except ValueError:
                print('Incorrect format.')
                continue
            if tp is int:
                if val != int(val):
                    print('Must be integer.')
                    continue
                val = int(val)
                if not (0 <= val < size):
                    print('Must >= 0 and < {}'.format(size))
                    continue
            val = tp(val)
            break
        data[field] = val
    return data

def convert_data_to_feature(data_item):
    feature = []
    for field, tp, size in features:
        d = data_item[field]
        if tp is int:
            for i in range(size):
                feature.append(float(i == d))
        elif tp is float:
            feature.append(float(d))
        else:
            raise NotImplementedError
    feature = torch.tensor(feature)
    return feature

input_size = sum(size for field, tp, size in features)

class Net(torch.nn.Module):
    def __init__(self, input_size, hidden_size):
        super(Net, self).__init__()

        self.layer1 = torch.nn.Linear(input_size, hidden_size)
        self.layer2 = torch.nn.Linear(hidden_size, 1)

    def forward(self, input):
        h = F.relu(self.layer1(input))
        logit = self.layer2(h).squeeze(-1)
        return logit

class DataItemSampler:
    def __init__(self):
        self.gender_dist = dist.bernoulli.Bernoulli(0.5)
        age_dense = [45, 45, 42, 41, 48, 63, 58, 48, 56, 62, 56, 43, 40, 31, 19, 14, 10, 8, 3, 1]
        age_dense = [age_dense[i // 5] for i in range(len(age_dense) * 5)]
        age_total = sum(age_dense)
        age_dense = [val / age_total for val in age_dense]
        self.age_dist = dist.categorical.Categorical(torch.tensor(age_dense))
        self.contact_history_dist = dist.bernoulli.Bernoulli(0.5)
        self.acid_test_dist = dist.bernoulli.Bernoulli(0.5)
        self.x_ray_dist = dist.bernoulli.Bernoulli(0.5)
        self.wbc_dist = dist.gamma.Gamma(9.0, 0.5)
        self.rbc_dist = dist.gamma.Gamma(9.0, 0.5)
        self.hgb_dist = dist.multivariate_normal.MultivariateNormal(
            torch.tensor([[140.0]]), torch.tensor([[20.0]]))

    def sample(self):
        score = 0.
        gender = self.gender_dist.sample().int().item()
        if gender == 0:
            score += 0.1
        else:
            score -= 0.1
        age = self.age_dist.sample().item()
        score += (age - 30) / 300.0
        contact_history = self.contact_history_dist.sample().int().item()
        if contact_history == 1:
            score += 0.5
        else:
            score -= 0.2
        acid_test = self.acid_test_dist.sample().int().item()
        if acid_test == 1:
            score += 10.0
        else:
            score -= 0.5
        x_ray = self.x_ray_dist.sample().int().item()
        if x_ray == 1:
            score += 100.
        else:
            score -= 1
        wbc = self.wbc_dist.sample().item()
        score += (4 - wbc) * 0.3
        rbc = self.rbc_dist.sample().item()
        score += (4 - rbc) * 0.2
        hgb = self.hgb_dist.sample().squeeze().item()
        score += (140 - hgb) * 0.2
        prob = torch.sigmoid(torch.tensor(score)).item()
        result = dist.bernoulli.Bernoulli(prob).sample().int().item()

        # data_item = {field: locals()[field] for field, tp, size in features}
        data_item = {
            'gender': gender,
            'age': age,
            'contact_history': contact_history,
            'acid_test': acid_test,
            'x_ray': x_ray,
            'wbc': wbc,
            'rbc': rbc,
            'hgb': hgb,
        }
        feature = convert_data_to_feature(data_item)

        print(data_item, prob, result)
        return feature, result

def make_dataset(sizes):
    data_item_sampler = DataItemSampler()
    return {stage: [data_item_sampler.sample() for i in range(size)] for stage, size in sizes.items()}

def estimate(net, data_item):
    input = convert_data_to_feature(data_item)
    logit = net(input)
    prob = torch.sigmoid(logit).item()
    return prob

def evaluate(net, dataset, batch_size, stage, threshold=0.5):
    dataloader = torch.utils.data.DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        drop_last=False,
    )
    net.eval()
    n_correct = 0
    n_total = 0
    for batch in dataloader:
        input, target = batch
        logit = net(input)
        prob = torch.sigmoid(logit)
        result = (prob >= threshold).int()
        correct = (result == target)
        n_correct += correct.sum().item()
        n_total += len(correct)
    accuracy = n_correct / n_total
    print('{} accuracy: {:.3%}'.format(stage, accuracy))
    return accuracy

def train(net, optimizer, dataset, n_epochs, batch_size, eval_batch_size):
    Loss = torch.nn.BCEWithLogitsLoss(reduction='mean')
    dataloader = torch.utils.data.DataLoader(
        dataset['train'],
        batch_size=batch_size,
        shuffle=True,
        drop_last=True,
    )
    net.train()
    try:
        for epoch_i in range(n_epochs):
            print('Epoch #{}:'.format(epoch_i))
            n_batch = 0
            sum_loss = 0.
            for batch_i, (input, target) in enumerate(dataloader):
                n_batch += 1
                optimizer.zero_grad()
                logit = net(input)
                loss = Loss(logit, target.float())
                sum_loss += loss.item()
                loss.backward()
                optimizer.step()
            mean_loss = sum_loss / n_batch
            print('mean loss: {}'.format(mean_loss))
            evaluate(net, dataset['valid'], eval_batch_size, 'valid')
            net.train()
    except KeyboardInterrupt:
        pass
    evaluate(net, dataset['test'], eval_batch_size, 'test')

def load_model():
    hidden_size = 20
    net = Net(input_size, hidden_size)
    net_state_dict, _ = torch.load('model.pt')
    net.load_state_dict(net_state_dict)
    return net

if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument('mode', choices=['train', 'eval'])
    argparser.add_argument('--seed', type=int)
    argparser.add_argument('--hidden_size', type=int, default=20)
    argparser.add_argument('--train_batch_size', type=int, default=16)
    argparser.add_argument('--eval_batch_size', type=int, default=128)
    argparser.add_argument('--lr', type=float, default=1e-3)
    argparser.add_argument('--n_epochs', type=int, default=20)
    argparser.add_argument('--load')
    argparser.add_argument('--save', default='model.pt')
    args = argparser.parse_args()

    if args.seed is not None:
        torch.manual_seed(args.seed)

    hidden_size = args.hidden_size

    net = Net(input_size, hidden_size)
    optimizer = torch.optim.Adam(net.parameters(), lr=args.lr)

    if args.mode == 'train':
        if args.load is not None:
            net_state_dict, optimizer_state_dict = torch.load(args.load)
            net.load_state_dict(net_state_dict)
            optimizer.load_state_dict(optimizer_state_dict)
        dataset = make_dataset({'train': 10000, 'valid': 1000, 'test': 1000})
        train(net, optimizer, dataset, args.n_epochs, args.train_batch_size, args.eval_batch_size)
        if args.save is not None:
            net_state_dict = net.state_dict()
            optimizer_state_dict = optimizer.state_dict()
            torch.save((net_state_dict, optimizer_state_dict), args.save)
    elif args.mode == 'eval':
        assert args.load is not None, "Must specify the path to load model"
        net_state_dict, optimizer_state_dict = torch.load(args.load)
        net.load_state_dict(net_state_dict)
        while True:
            data = read_data()
            prob = estimate(net, data)
            print('estimated probability: {:.3%}'.format(prob))
