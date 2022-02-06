"""

This class is used to create the underlying smooth surfaces (terrains) for the 
experiment. This is done by taking a random sample from a 2d-function prior with
0 mean, having a Radial Basis Kernel with a given lengthscale to control for the 
variation of the terrain.

In addition, it selects which of the tiles on the grid would be revealed
to the subject, and based on those, trains the Gaussian process with those 
revealed values. Then, it finds the value of the variance at all of the locations,
to see which positions of the terrain the trained Gaussian process (which knows
nothing about the underlying surface except for those tiles revealed to it) has 
the most uncertainty about.

This uses the gpytorch module.

"""

import numpy as np
import matplotlib.pyplot as plt
import torch
import json
import gpytorch
import torch.distributions as dist
from gpytorch.mlls.variational_elbo import VariationalELBO
from gpytorch.models import AbstractVariationalGP
from gpytorch.variational import CholeskyVariationalDistribution
from gpytorch.variational import VariationalStrategy


RANDOM_STATE=np.random.randint(200);
RANDOM_STATE=9;
torch.manual_seed(RANDOM_STATE);

# Create the GP Model as an exact GP
class ExactGPModel(gpytorch.models.ExactGP):
    def __init__(self, train_x, train_y, likelihood, lengthscale):
        super(ExactGPModel, self).__init__(train_x, train_y, likelihood)
        self.mean_module = gpytorch.means.ConstantMean()
        rbf = gpytorch.kernels.RBFKernel();
        rbf._set_lengthscale(lengthscale);
        self.covar_module = gpytorch.kernels.ScaleKernel(rbf);
        print(self.covar_module);
    
    def forward(self, x):
        mean_x = self.mean_module(x)
        covar_x = self.covar_module(x)
        return gpytorch.distributions.MultivariateNormal(mean_x, covar_x)

# Initialze the lengthscale

lengthscale = torch.tensor([40.0]);
# Initialize likelihood and model
likelihood = gpytorch.likelihoods.GaussianLikelihood()
prior_model = ExactGPModel(None, None, likelihood, lengthscale)

# Create a grid to sample the surface at even intervals
bounds = (0,100);
n = 8
grid = torch.zeros(n ** 2, 2)
axpoints = torch.linspace(bounds[0], bounds[1], n)
grid[:, 0].copy_(axpoints.repeat(n))
grid[:, 1].copy_(axpoints.unsqueeze(1).repeat(1, n).view(-1))

prior_model.eval()
likelihood.eval();

# Sample a function from the zero mean GP Prior
with torch.no_grad():
    post_f = prior_model(grid);
    mean = post_f.mean;
    var = post_f.variance;
    sample = post_f.sample();

# Pick a number of points at random that are to be revealed
num_revealed = 4;
perm = torch.randperm(sample.size(0));
revealed_idx = perm[:num_revealed];
train_y = sample[revealed_idx];
train_x = grid[revealed_idx];

# Train the zero prior GP model on these points
trained_model = ExactGPModel(train_x, train_y, likelihood, lengthscale);

# Find optimal model hyperparameters
training_iter = 100;
trained_model.train()
likelihood.train()

# Use the adam optimizer
optimizer = torch.optim.Adam([
    {'params': trained_model.parameters()},
    #{'params': trained_model.likelihood.parameters()}  # Includes GaussianLikelihood parameters
], lr=0.1)

# "Loss" for GPs - the marginal log likelihood
mll = gpytorch.mlls.ExactMarginalLogLikelihood(likelihood, trained_model)

for i in range(training_iter):
    # Zero gradients from previous iteration
    optimizer.zero_grad()
    # Output from model
    output = trained_model(train_x)
    # Calc loss and backprop gradients
    loss = -mll(output, train_y)
    loss.backward()
    #print('Iter %d/%d - Loss: %.3f   lengthscale: %.3f   noise: %.3f' % (
    #    i + 1, training_iter, loss.item(),
    #    trained_model.covar_module.base_kernel.lengthscale.item(),
    #    trained_model.likelihood.noise.item()
    #))
    optimizer.step()

trained_model.eval();
likelihood.eval();

# Get the posterior of the GP, which contains the variance (uncertainty)
#   information at each point on the grid
post_f = likelihood(trained_model(grid));
mean = post_f.mean;
var = post_f.variance;

uncertainty_variance = (var.std() ** 2).item();

"""
plt.figure()
pcm = plt.pcolormesh(axpoints.numpy(), axpoints.numpy(), mean.reshape(n,n).detach().numpy(), cmap=cmap);
plt.title('Predictive Mean');

plt.figure()
pcm = plt.pcolormesh(axpoints.numpy(), axpoints.numpy(), var.reshape(n,n).detach().numpy(), cmap=cmap)
plt.title('Predictive Variance');

plt.show();

print(mean);
print(mean[idx]);
print(var);
print(var[idx]);
"""
def scale_to_range(tensor, newmin, newmax):
    min_ = tensor.min();
    max_ = tensor.max();
    tensor = ((tensor - min_) * newmax / (max_ - min_)) + newmin;
    tensor = tensor.round().int();
    return tensor

def scalar_to_2dindex(idx, n):
	idx1 = int(idx / n);
	idx2 = (idx % n).item();
	return (idx1, idx2);


# Scale values and convert all necessary values to JSON format
var = var.reshape(n,n);
sample = sample.reshape(n,n);
sample = scale_to_range(sample, 0, 99);

json_dict = {};

revealed_idx = [scalar_to_2dindex(idx, n) for idx in revealed_idx]
json_dict['revealed_idx'] = revealed_idx;
json_dict['uncertainty_variance'] = uncertainty_variance;
json_dict['gridvals'] = sample.tolist();
json_dict['variances'] = var.tolist();

# Write JSON to file
with open('../valdicts/sample{}.json'.format(RANDOM_STATE), 'w') as f_out:
    f_out.write(json.dumps(json_dict));



"""
def tensor_to_dict(tensor):
    dict_ = {};
    size_ = tensor.shape;
    for i in range(size_[0]):
        for j in range(size_[1]):
            idx = str(j)+","+str(i);
            dict_[idx] = tensor[i,j].item();
    return dict_;

print(grid);

dict_ = tensor_to_dict(sample);
with open('valdict6.json', 'w') as f_out:
        f_out.write(json.dumps(dict_));

cmap = plt.get_cmap('jet');

pcm = plt.pcolormesh(axpoints.numpy(), axpoints.numpy(), sample.reshape(n,n).numpy(), cmap=cmap);
plt.show();
"""