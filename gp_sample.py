import numpy as np
import matplotlib.pyplot as plt
import torch
import gpytorch
from gpytorch.mlls.variational_elbo import VariationalELBO
from gpytorch.models import AbstractVariationalGP
from gpytorch.variational import CholeskyVariationalDistribution
from gpytorch.variational import VariationalStrategy

torch.manual_seed(4);

class ExactGPModel(gpytorch.models.ExactGP):
    def __init__(self, train_x, train_y, likelihood, lengthscale):
        super(ExactGPModel, self).__init__(train_x, train_y, likelihood)
        self.mean_module = gpytorch.means.ConstantMean()
        self.covar_module = gpytorch.kernels.ScaleKernel(gpytorch.kernels.RBFKernel(lengthscale=lengthscale))
    
    def forward(self, x):
        mean_x = self.mean_module(x)
        covar_x = self.covar_module(x)
        return gpytorch.distributions.MultivariateNormal(mean_x, covar_x)

lengthscale = 10;
# initialize likelihood and model
likelihood = gpytorch.likelihoods.GaussianLikelihood()
model = ExactGPModel(None, None, likelihood, lengthscale)

bounds = (0,100);
n = 200
grid = torch.zeros(n ** 2, 2)
axpoints = torch.linspace(bounds[0], bounds[1], n)
grid[:, 0].copy_(axpoints.repeat(n))
grid[:, 1].copy_(axpoints.unsqueeze(1).repeat(1, n).view(-1))

post_f = model.forward(grid);
mean = post_f.mean;
var = post_f.variance;

sample = post_f.sample();

print(grid);
print(sample);
print(sample.reshape(n,n));

cmap = plt.get_cmap('jet');

pcm = plt.pcolormesh(axpoints.numpy(), axpoints.numpy(), sample.reshape(n,n).numpy(), cmap=cmap);
plt.show();