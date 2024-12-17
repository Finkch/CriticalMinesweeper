# Parallel Minesweeper
#
# Uses the powers of tensors to do things a bit quicker.
# However, likely due to Python being Python, it moves data between the device
# and the CPU every iteration. This is very slow so we use the CPU instead of the GPU.

import torch

def minesweeper(rho: float, s: int, d: int, device: torch.device = None) -> list[float]:

    # Default device
    if not device:
        device = torch.device("cpu")

    # Makes the grid size odd so that it has a centre
    d = int(d) + 1

    # A kernal to quickly calculate neighbours.
    adj_kernal = torch.tensor([[1, 1, 1], [1, 0, 1], [1, 1, 1]], dtype = torch.float32, device = device).unsqueeze(0).unsqueeze(0)

    # Centre of the grid
    c = d // 2

    # Tensors to track state
    mines       = (torch.rand((d, d), device = device) < rho).to(torch.bool)
    unrevealed  = lnot((torch.zeros_like(mines, device = device)))
    frontier    = torch.zeros_like(mines, device = device)

    # Creates a starting zone with no mines
    mines[c - s : c + s + 1, c - s : c + s + 1] = False

    # Find cells not adjacent to a mine
    zeroes      = lnot(adj(mines, adj_kernal))

    # Initial reveal
    frontier[c][c] = True


    # Propogates while there is a frontier
    unrevealed, sizes = sweep(frontier, unrevealed, zeroes, adj_kernal)

    # To calculate number of reveals, first find revealed cells
    revealed = lnot(unrevealed)

    # Second, include all non-zero neighbours.
    # As is, we only reveal zero-valued cells hence the extra step to
    # include neighbours which are guaranteed to be nonzeroes.
    # Even though this adj_matrix does not include the own cell, this problem is
    # by its nature contiguous so unless r = 1, it will return equivalent results.
    revealed = adj(revealed, adj_kernal)

    # Counts total cells
    reveals = torch.sum(revealed).item()

    # Return results
    return reveals, sizes


# Precompiles tensor operations
# Truth be told, the precompilation is probably doing nothing in these tiny functions.

@torch.jit.script
def adj(cells: torch.Tensor, kernel: torch.Tensor) -> torch.Tensor:
    return torch.nn.functional.conv2d(
        cells.unsqueeze(0).unsqueeze(0).float(),
        kernel,
        padding=1
    ).squeeze(0).squeeze(0).to(torch.bool)

@torch.jit.script
def lnot(tensor: torch.Tensor) -> torch.Tensor:
    return torch.logical_not(tensor)

@torch.jit.script
def sweep(frontier: torch.Tensor, unrevealed: torch.Tensor, zeroes: torch.Tensor, adj_kernal: torch.Tensor):

    # Used to track alpha.
    # Silly large tensor because script requires not-mutable data structures.
    # And yes, this size of tensor is guaranteed to have sufficient space
    sizes = torch.zeros(int(frontier.size()[0] ** 2 / 2), dtype = torch.int32, device = frontier.device)
    i = 0

    # Sweep until the frontier wave-front goes exctinct
    while frontier.any():

        # Adds 
        sizes[i] = torch.sum(frontier).item()
        i += 1

        # Updates revealed cells
        unrevealed ^= frontier


        # Compute neighbours of the current frontier
        neighbours = torch.nn.functional.conv2d(
            frontier.unsqueeze(0).unsqueeze(0).float(),
            adj_kernal,
            padding=1
        ).squeeze(0).squeeze(0).to(torch.bool)


        # Propogates the wavefront.
        # We can ignore cells with a mine since they are encloses by 
        # nonzeroes and thus unreachable anyways.
        # Equivalent to: frontier = neighbours & unrevealed & zeroes & ~mines
        frontier = neighbours & unrevealed & zeroes


    # Trims off all right-hand zeroes but the first.
    # Guaranteed to be at least once since the 1d tensor is overkill-sized
    sizes = sizes[ : (sizes == 0).nonzero()[0][0].item() + 1]

    return unrevealed, sizes

#       END Precompiled tensoro operations



#   Experiemnts = 10
#   Trials      = 100
#   Cutoff      = 10000
#   Density     = 0.05

#       CPU
# Time to benchmark...starting point:
# .. Total time:  5.058522939682007
# .. Mean time:   0.5058522939682006
# .. Min time:    0.4986269474029541
# .. Max time:    0.5101470947265625
#
# Different casting technique:
# .. Total time:  5.197870969772339
# .. Mean time:   0.5197870969772339
# .. Min time:    0.5049571990966797
# .. Max time:    0.5550258159637451
#
#       GPU
# Starting point
# .. Total time:  41.477593421936035
# .. Mean time:   4.147759342193604
# .. Min time:    4.016181945800781
# .. Max time:    4.318481206893921


# Torch methods instead of Python operators
#       CPU
# .. Total time:  4.923171758651733
# .. Mean time:   0.4923171758651733
# .. Min time:    0.47390103340148926
# .. Max time:    0.5548911094665527
#
#       GPU
# .. Total time:  45.84257626533508
# .. Mean time:   4.584257626533509
# .. Min time:    4.319262981414795
# .. Max time:    5.203902006149292

# Minimising NOT operations
#       CPU
# .. Total time:  2.6851351261138916
# .. Mean time:   0.26851351261138917
# .. Min time:    0.25437116622924805
# .. Max time:    0.3008742332458496
#
#       GPU
# .. Total time:  32.242626667022705
# .. Mean time:   3.2242626667022707
# .. Min time:    3.0139272212982178
# .. Max time:    3.5307891368865967

# Combining mineless and zeroes.
# Really, not faster? We're doing less calculations a step! Huh...
# .. Total time:  2.6831047534942627
# .. Mean time:   0.26831047534942626
# .. Min time:    0.262772798538208
# .. Max time:    0.27779698371887207
#
# .. Total time:  34.143808126449585
# .. Mean time:   3.4143808126449584
# .. Min time:    3.2541279792785645
# .. Max time:    3.60793399810791

# Not summing to obtain reveals.
# Not surprising that there's no change given we do this once.
#       CPU
# .. Total time:  2.7044496536254883
# .. Mean time:   0.2704449653625488
# .. Min time:    0.2677910327911377
# .. Max time:    0.27472400665283203
#
#       GPU
# .. Total time:  34.51270127296448
# .. Mean time:   3.4512701272964477
# .. Min time:    3.174008846282959
# .. Max time:    3.8604259490966797

# Alternative safe-zone creation
#       CPU
# .. Total time:  2.704470157623291
# .. Mean time:   0.2704470157623291
# .. Min time:    0.26561403274536133
# .. Max time:    0.27668023109436035
#
#       GPU
# .. Total time:  33.701714754104614
# .. Mean time:   3.3701714754104612
# .. Min time:    3.1892948150634766
# .. Max time:    3.699763059616089

# Going back to operator-based frontier updates
#       CPU
# .. Total time:  2.718647003173828
# .. Mean time:   0.2718647003173828
# .. Min time:    0.265765905380249
# .. Max time:    0.2786829471588135
#
#       GPU
# .. Total time:  28.717310190200806
# .. Mean time:   2.8717310190200807
# .. Min time:    2.6966028213500977
# .. Max time:    2.985135078430176

# Precompiled tensor operations.
# Hm. Less impactfull than I was expecting.
#        CPU
# .. Total time:  2.7036898136138916
# .. Mean time:   0.27036898136138915
# .. Min time:    0.26676201820373535
# .. Max time:    0.2753181457519531
#
#       GPU
# .. Total time:  27.903862237930298
# .. Mean time:   2.7903862237930297
# .. Min time:    2.695000171661377
# .. Max time:    2.8710060119628906

# Mostly using operators rather than precompiled operations
#        CPU
# .. Total time:  3.093524694442749
# .. Mean time:   0.3093524694442749
# .. Min time:    0.3033740520477295
# .. Max time:    0.33611512184143066
#
#        GPU
# .. Total time:  27.54062247276306
# .. Mean time:   2.7540622472763063
# .. Min time:    2.6549179553985596
# .. Max time:    2.8661937713623047

# More precompiled, more torch.logical_*.
# It looks like GPU benefits from in-place operations whereas
# cpu benefits from torch.logical_* operations.
#        CPU
# .. Total time:  2.704416036605835
# .. Mean time:   0.2704416036605835
# .. Min time:    0.265578031539917
# .. Max time:    0.2755589485168457
#
#        GPU
# .. Total time:  32.668092250823975
# .. Mean time:   3.2668092250823975
# .. Min time:    3.1706619262695312
# .. Max time:    3.526344060897827

# Using while i < d
#        CPU
# .. Total time:  3.0802602767944336
# .. Mean time:   0.30802602767944337
# .. Min time:    0.30588507652282715
# .. Max time:    0.3109879493713379
#
#        GPU
# .. Total time:  17.265538692474365
# .. Mean time:   1.7265538692474365
# .. Min time:    1.6747570037841797
# .. Max time:    1.8693318367004395

# Alternative loop condition
#        CPU
# .. Total time:  2.8323562145233154
# .. Mean time:   0.28323562145233155
# .. Min time:    0.2771110534667969
# .. Max time:    0.2890958786010742
#
#        GPU
# .. Total time:  33.61609411239624
# .. Mean time:   3.361609411239624
# .. Min time:    3.12271785736084
# .. Max time:    3.7901298999786377

# A note not a benchmark.
# Hm, I tried increasing max_r by 100 and the GPU is WAAAAY slower than 100x.
# This seems to confirm my suspicions that each while loop sees the data being moved
# back and forth. Why? Other than the loop condition, there should be no reason to have
# in on the CPU; how can I keep it on the far side?
#
# Of course, if it's on the CPU, increasing max_r also really sucks beacuse it requires
# d ** 2 operations per iterations, even when most of them are empty cells! Pah!

# Script while loop as a whole
#        CPU
# .. Total time:  2.473433017730713
# .. Mean time:   0.2473433017730713
# .. Min time:    0.2453148365020752
# .. Max time:    0.24932312965393066
#
#        GPU
# .. Total time:  26.302876234054565
# .. Mean time:   2.6302876234054566
# .. Min time:    2.5510339736938477
# .. Max time:    2.8086280822753906

# Scripted sweep with tensor functions.
# Huh, only impacted mps times...
#        CPU
# .. Total time:  2.454509973526001
# .. Mean time:   0.2454509973526001
# .. Min time:    0.2423691749572754
# .. Max time:    0.24864411354064941
#
#        GPU
# .. Total time:  32.56902885437012
# .. Mean time:   3.256902885437012
# .. Min time:    3.1360888481140137
# .. Max time:    3.6079540252685547

# Quick comparison between serial and parallel as cutoff increases.
# Since we're stuck on the CPU, tensors become a worse choice as cutoff increases.
# Oh! My expectation was proven wrong! I was thinking that the original method grew closer
# to linearly whereas tensors were stuck at d^2; while that may still be the case, tensors are
# still so blazingly fast that at these cutoffs they still easily outperform.
#   Experiemnts = 10
#   Trials      = 100
#   Cutoff      = 1000000
#   Density     = 0.05
#
#       Serial
# .. Total time:          6371.8884s
# .. Mean time:           637.1888s
# .. Minimum time:        642.2508s
# .. Maximum time:        638.5931s
#
#       Parallel
# .. Total time:  1346.597899198532
# .. Mean time:   134.6597899198532
# .. Min time:    134.0677900314331
# .. Max time:    135.1642129421234

# Back to the normal benchmark:
#   Experiemnts = 10
#   Trials      = 100
#   Cutoff      = 10000
#   Density     = 0.05
#
#       CPU
#   Uh, whoops. Normal times about 0.24.

# Tracking sizes of successive frontiers
#       CPU
# .. Total time:          3.1366s
# .. Mean time:           0.3137s
# .. Minimum time:        0.3322s
# .. Maximum time:        0.3111s

# Trimming sizes tensor
#       CPU
# .. Total time:          3.1811s
# .. Mean time:           0.3181s
# .. Median time:         0.3127s
# .. Minimum time:        0.3572s
# .. Maximum time:        0.3024s

# Trimming within jit; removing "as_tuple"
#       CPU
# .. Total time:          3.1842s
# .. Mean time:           0.3184s
# .. Median time:         0.3142s
# .. Minimum time:        0.3427s
# .. Maximum time:        0.3081s

# Removing saftey check of trimming (since there is guaranteed to be a zero)
#       CPU
# .. Total time:          3.1255s
# .. Mean time:           0.3125s
# .. Median time:         0.3306s
# .. Minimum time:        0.3819s
# .. Maximum time:        0.2997s