{
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "zmbEjOEctF5L"
      },
      "source": [
        "# Machine Learning Systems Assignment 2\n",
        "\n",
        "<a target=\"_blank\" href=\"https://colab.research.google.com/github/mlsyscourse/assignment2/blob/main/mlsys_hw2.ipynb\">\n",
        "  <img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/>\n",
        "</a>\n",
        "\n",
        "**Assignment due: Feb 26, 2025, 11:59 pm, Eastern Time**.\n",
        "\n",
        "Tensor program optimization is a very important part in machine learning compilation.\n",
        "It enables operators in machine learning (e.g., matrix multiplication, convolution, reduction, etc.)\n",
        "to run efficiently on various modern hardware.\n",
        "In this assignment, you will use a tensor program optimizing interface in [TVM](https://tvm.apache.org)\n",
        "to schedule and automatically tune typical operators.\n",
        "\n",
        "* **Be prepared** -- in this assignment you may need to learn many new terminologies and concepts.\n",
        "* You should work on this assignment **individually** -- it is not a team assignment.\n",
        "* This assignment **requires** NVIDIA GPU with CUDA environment. You can do the assignment on Google Colab (by clicking the badge above) or any other GPU server that you have access to. **Important note: we will test your submission with an NVIDIA T4 GPU, which is free available on Google Colab. So if you do the assignment on other environments, we recommend you to test it on Colab before submission.**\n",
        "* This assignment is pure Python. No C++ is needed in this assignment.\n",
        "* Please check out the end of this notebook for the assignment submission requirement.\n",
        "* Please do not share your solution on publicly available websites (e.g., GitHub).\n",
        "* **About testing and grading.** The assignment will be automatically graded. You can submit multiple times, and the time stamp of that submission will be used in determining any late penalties. We also encourage you to create your own test cases, which helps you confirm the correctness of your code.\n"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "GYQEg5aGtF5N"
      },
      "source": [
        "## Preparation\n",
        "\n",
        "### Using Google Colab\n",
        "\n",
        "If you are using Google Colab environment, please make a copy of this notebook file by selecting \"Save a copy in Drive\" from the \"File\" menu, and then run the code block below to set up workspace. After cloning, you will see the cloned repository in the \"Files\" bar on the left."
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "JWVB-ZKRtF5O"
      },
      "outputs": [],
      "source": [
        "# Code to set up the assignment\n",
        "from google.colab import drive\n",
        "drive.mount('/content/drive')\n",
        "%cd /content/drive/MyDrive/\n",
        "!mkdir -p 15442\n",
        "%cd /content/drive/MyDrive/15442\n",
        "!git clone https://github.com/mlsyscourse/assignment2.git\n",
        "%cd /content/drive/MyDrive/15442/assignment2"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "16sPai6ftF5P"
      },
      "source": [
        "Then run the following cell to install TVM dependency.\n",
        "\n",
        "**Note.** The PyPI package installed below only has CPU support.\n",
        "It is fine to use this CPU package when you implement the\n",
        "first five tasks of part 1.\n",
        "We will have instructions on how to install the GPU package\n",
        "later on."
      ]
    },
    {
      "cell_type": "code",
      "execution_count": 7,
      "metadata": {
        "id": "CWK_sDGVtF5P",
        "outputId": "098da88d-dcbf-4c40-abd5-00490a86dee6",
        "colab": {
          "base_uri": "https://localhost:8080/"
        }
      },
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            "Looking in links: https://mlc.ai/wheels\n",
            "Requirement already satisfied: mlc-ai-cpu in /usr/local/lib/python3.11/dist-packages (0.19.0)\n",
            "Requirement already satisfied: attrs in /usr/local/lib/python3.11/dist-packages (from mlc-ai-cpu) (25.1.0)\n",
            "Requirement already satisfied: cloudpickle in /usr/local/lib/python3.11/dist-packages (from mlc-ai-cpu) (3.1.1)\n",
            "Requirement already satisfied: decorator in /usr/local/lib/python3.11/dist-packages (from mlc-ai-cpu) (4.4.2)\n",
            "Requirement already satisfied: ml-dtypes in /usr/local/lib/python3.11/dist-packages (from mlc-ai-cpu) (0.4.1)\n",
            "Requirement already satisfied: numpy in /usr/local/lib/python3.11/dist-packages (from mlc-ai-cpu) (1.26.4)\n",
            "Requirement already satisfied: packaging in /usr/local/lib/python3.11/dist-packages (from mlc-ai-cpu) (24.2)\n",
            "Requirement already satisfied: psutil in /usr/local/lib/python3.11/dist-packages (from mlc-ai-cpu) (5.9.5)\n",
            "Requirement already satisfied: scipy in /usr/local/lib/python3.11/dist-packages (from mlc-ai-cpu) (1.13.1)\n",
            "Requirement already satisfied: tornado in /usr/local/lib/python3.11/dist-packages (from mlc-ai-cpu) (6.4.2)\n",
            "Requirement already satisfied: typing-extensions in /usr/local/lib/python3.11/dist-packages (from mlc-ai-cpu) (4.12.2)\n"
          ]
        }
      ],
      "source": [
        "!python3 -m pip install mlc-ai-cpu -f https://mlc.ai/wheels"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "OcykIcMAtF5P"
      },
      "source": [
        "We can validate that the dependency is successfully installed by running the following."
      ]
    },
    {
      "cell_type": "code",
      "execution_count": 8,
      "metadata": {
        "id": "-GQ--1ZTtF5P",
        "outputId": "256b412a-e00b-460e-d871-321574a9fdcf",
        "colab": {
          "base_uri": "https://localhost:8080/"
        }
      },
      "outputs": [
        {
          "output_type": "execute_result",
          "data": {
            "text/plain": [
              "['/usr/local/lib/python3.11/dist-packages/tvm']"
            ]
          },
          "metadata": {},
          "execution_count": 8
        }
      ],
      "source": [
        "import tvm\n",
        "tvm.__path__"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "eBKcg-KxtF5Q"
      },
      "source": [
        "### Using local environment\n",
        "\n",
        "If you are using local/server environment (requiring NVIDIA GPU and CUDA ≥ 11.7), please clone this repository.\n",
        "\n",
        "```shell\n",
        "git clone https://github.com/mlsyscourse/assignment2.git\n",
        "cd assignment2\n",
        "export PYTHONPATH=$PWD:$PYTHONPATH\n",
        "```\n",
        "\n",
        "We recommend you to create a conda environment and install the dependency package in the environment.\n",
        "```shell\n",
        "conda create --name 15442 python=3.11\n",
        "conda activate 15442\n",
        "python3 -m pip install --force-reinstall mlc-ai-cu123 -f https://mlc.ai/wheels\n",
        "```"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "NVmxJjx7tF5Q"
      },
      "source": [
        "Please also select the Python interpreter in this conda environment and use it to run this notebook.\n",
        "We can validate that the dependency is successfully installed by running the following."
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "wLYZaYCwtF5R",
        "outputId": "c3edf56b-18e4-4751-8bc3-730c5a1b4088"
      },
      "outputs": [
        {
          "data": {
            "text/plain": [
              "['/path/to/conda/envs/15442/lib/python3.11/site-packages/tvm']\n"
            ]
          },
          "execution_count": 1,
          "metadata": {},
          "output_type": "execute_result"
        }
      ],
      "source": [
        "import tvm\n",
        "tvm.__path__"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "EAdmjK7_tF5R"
      },
      "source": [
        "## Part 1. Optimize Matrix Multiplication (80 pt)\n",
        "\n",
        "In part 1, you will manually optimize a fused \"GeMM + ReLU + add\" operator with TVM and run it\n",
        "on the NVIDIA GPU in your environment.\n",
        "The \"GeMM + ReLU + add\" pattern is common in machine learning models when activation\n",
        "and residual-add operations are involved.\n",
        "Formally, for given 2-dim tensors $A$, $B$, and $C$, we want to compute the following $D$:\n",
        "\n",
        "$$\n",
        "D = \\mathrm{ReLU} (A B) + C.\n",
        "$$"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "lBIet5y0tF5R"
      },
      "source": [
        "We define this operator using [TensorIR](https://arxiv.org/pdf/2207.04296.pdf),\n",
        "the tensor program level intermediate representation (IR) in TVM, as follows.\n",
        "You can also find this definition in `gemm_relu_add.py`."
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "VWC2ThyitF5R"
      },
      "source": [
        "```python\n",
        "from tvm import tir\n",
        "from tvm.script import tir as T\n",
        "\n",
        "M = 2048\n",
        "N = 2048\n",
        "K = 2048\n",
        "\n",
        "\n",
        "@T.prim_func\n",
        "def gemm_relu_add(\n",
        "    A: T.Buffer((M, K), \"float32\"),\n",
        "    B: T.Buffer((K, N), \"float32\"),\n",
        "    C: T.Buffer((M, N), \"float32\"),\n",
        "    D: T.Buffer((M, N), \"float32\"),\n",
        ") -> None:\n",
        "    matmul = T.alloc_buffer((M, N), \"float32\", scope=\"global\")\n",
        "    relu = T.alloc_buffer((M, N), \"float32\", scope=\"global\")\n",
        "    # Compute GeMM\n",
        "    for i, j, k in T.grid(M, N, K):\n",
        "        with T.block(\"gemm\"):\n",
        "            vi = T.axis.spatial(M, i)\n",
        "            vj = T.axis.spatial(N, j)\n",
        "            vk = T.axis.reduce(K, k)\n",
        "            with T.init():\n",
        "                matmul[vi, vj] = T.float32(0)\n",
        "            matmul[vi, vj] += A[vi, vk] * B[vk, vj]\n",
        "    # Compute ReLU\n",
        "    for i, j in T.grid(M, N):\n",
        "        with T.block(\"relu\"):\n",
        "            vi = T.axis.spatial(M, i)\n",
        "            vj = T.axis.spatial(N, j)\n",
        "            relu[vi, vj] = T.max(matmul[vi, vj], T.float32(0))\n",
        "    # Compute add\n",
        "    for i, j in T.grid(M, N):\n",
        "        with T.block(\"add\"):\n",
        "            vi = T.axis.spatial(M, i)\n",
        "            vj = T.axis.spatial(N, j)\n",
        "            D[vi, vj] = relu[vi, vj] + C[vi, vj]\n",
        "\n",
        "\n",
        "sch = tir.Schedule(gemm_relu_add)\n",
        "```"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "ZTxXVI7QtF5R"
      },
      "source": [
        "Let's go through this piece of code and look into its components.\n",
        "\n",
        "* The function takes the four tensors `A`, `B`, `C` and `D` as inputs with the corresponding shape and dtype.\n",
        "You may notice that the tensor `D`, which we want to compute, is passed in as an argument, rather than\n",
        "a function return value.\n",
        "This is what we call the \"destination-passing style,\" where we allocate the destination tensor\n",
        "before calling this function, and pass in the destination tensor as an argument.\n",
        "Destination-passing style is widely adopted by low-level operator libraries (e.g.,\n",
        "[cuBLAS](https://docs.nvidia.com/cuda/cublas/index.html)) and the tensor program level\n",
        "abstractions in machine learning compilers.\n",
        "* The first two lines of the function body define the tensors where intermediate results from\n",
        "GeMM and ReLU are stores. Their memory scope is global at this moment.\n",
        "* Next, there are the three sequential for-loop blocks defining the computation.\n",
        "  * The first one defines the GeMM computation. For a given `vi` and `vj`, the loop body\n",
        "  reads from `A` and `B`, sums up the values along `vk`, and stores the summation result into\n",
        "  the intermediate tensor `matmul`, with `T.float32(0)` being the initial value of the summation.\n",
        "  * The second one defines the ReLU computation, which element-wisely takes the maximum\n",
        "  of `matmul` and zero.\n",
        "  * The third one describes the element-wise addition of the ReLU result and the input tensor `C`.\n",
        "* After defining the function, we create a `tir.Schedule` instance with regard to this function.\n",
        "`tir.Schedule` is the core tool in this assignment you will use to optimize this function.\n",
        "`tir.Schedule` provides the a set of function transformations (which we call \"schedule primitives\")\n",
        "that help accelerate the function execution on hardware.\n",
        "We will introduce these schedule primitives later."
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "c2XJs4KMtF5R"
      },
      "source": [
        "Your goal in this part is to optimize this GeMM + ReLU + add workload so that it can efficiently run on GPU.\n",
        "Usually, optimizing such a workload of matrix multiplication with epilogues (e.g., ReLU and add here)\n",
        "for GPU, five major steps are required:\n",
        "\n",
        "1. shared memory tiling,\n",
        "2. register tiling,\n",
        "3. cooperative fetching,\n",
        "4. write cache.\n",
        "5. epilogue fusion.\n",
        "\n",
        "Before you start, here is a note on grading.\n",
        "When grading your submission in this part, we evaluate your optimization from two aspects.\n",
        "* The first and most basic one is the **numerical correctness**.\n",
        "This being said, after optimizing the workload, your function should produce the\n",
        "same numerical results as the original workload.\n",
        "More concretely, in this assignment, it means that the function after your optimization\n",
        "should still compute GeMM + ReLU + addition.\n",
        "We provide the tests for you to check the numerical correctness of your optimization.\n",
        "But you may not be able to run the test until you have implemented all optimizations.\n",
        "* The other aspect is whether you properly implemented the optimizations.\n",
        "Unfortunately, it is hard to automatically check this,\n",
        "and **there is no test** for you to test it in Python.\n",
        "Your submission will be **manually** checked to see if each task is properly implemented.\n",
        "On the other hand, we provide the optimized function after **finishing all five tasks** in `reference.py` for your reference.\n",
        "So you can see what a final function may look like,\n",
        "and you can also refer to it after you implementing each task.\n",
        "*Please note that you do not have to get the exactly same function as the reference one.*\n"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "OaTw0JsMtF5R"
      },
      "source": [
        "Now, let's get started."
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "GXTmhN8-tF5R"
      },
      "source": [
        "### Task 1. Shared memory tiling (20 pt)\n",
        "\n",
        "Our optimization is centered around the GeMM part.\n",
        "This is because though we have three stages (GeMM, ReLU and add) in this workload,\n",
        "GeMM has the the heaviest computation and the most memory accesses.\n",
        "Once we have optimized the GeMM, the rest parts can be optimized accordingly,\n",
        "based on how the GeMM is optimized.\n",
        "\n",
        "You have learned about the concept of **thread blocks** in GPU architectures from the lectures.\n",
        "To optimize a GeMM workload, people usually partition the destination matrix (`matmul` for our case)\n",
        "into multiple tiles along both the row and column dimensions, and assign one thread block\n",
        "for the computation of each tile.\n",
        "\n",
        "For example, in the figure below, a thread block computes a `(tile_x, tile_y)` tile.\n",
        "That is to say, this particular thread block will iterate over a `(tile_x, K)` region of `A`\n",
        "and a `(K, tile_y)` region of `B`, compute the matrix multiplication of these two regions,\n",
        "and write the results into the `(tile_x, tile_y)` tile.\n",
        "We can use Python notation to formally describe the tiling:\n",
        "for a given thread block, assuming the tile that this thread block computes\n",
        "starts from `offset_x` on the `M` dimension and `offset_y` on the `N` dimension,\n",
        "then the thread block computes the following:\n",
        "```python\n",
        "matmul[offset_x : offset_x + tile_x, offset_y : offset_y + tile_y] = (\n",
        "    A[offset_x : offset_x + tile_x, :] @ B[:, offset_y : offset_y + tile_y]\n",
        ")\n",
        "```\n",
        "\n",
        "<img src=\"https://raw.githubusercontent.com/mlsyscourse/assignment2/main/figure/shared-memory-tiling.jpg\" alt=\"figure/shared-memory-tiling.jpg\" width=\"100%\">"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "VswkvHyqtF5S"
      },
      "source": [
        "The next step is about reducing the memory access pressure of the GeMM operator.\n",
        "This is done via leveraging **shared memory** available in GPU, which you also learned about from lectures:\n",
        "rather than directly reading from `A` and `B` (which reside in global memory)\n",
        "at the time of computing multiplication, each thread block first loads the `A` region\n",
        "and `B` region it needs from global memory to shared memory.\n",
        "\n",
        "Just like CPU cache, while shared memory can offer much faster access speed,\n",
        "it has relatively smaller size than global memory.\n",
        "Usually, the size of shared memory available in a thread block is no more than 48KB.\n",
        "In our case, given each float32 element has four bytes,\n",
        "the `A` region and `B` region that a thread block needs\n",
        "have size `(tile_x * K * 4) + (tile_y * K * 4)` bytes.\n",
        "which is far more than the available shared memory size a thread block can use.\n",
        "To address this issue, you also need split the long stripe of `A` and `B` into\n",
        "multiple chunks along the `K` dimension.\n",
        "By doing this, now you are able to go through `A` chunks and `B` chunks one at a time simultaneously,\n",
        "and load a single `A` tile and `B` chunk into shared memory, which fits the available\n",
        "shared memory size.\n",
        "This can be formally written as\n",
        "\n",
        "```python\n",
        "matmul[offset_x : offset_x + tile_x, offset_y : offset_y + tile_y] = sum(\n",
        "    A[offset_x : offset_x + tile_x, k : k + tile_k]\n",
        "    @ B[k : k + tile_k, offset_y : offset_y + tile_y]\n",
        "    for k in range(0, n, tile_k)\n",
        ")\n",
        "```\n"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "gv5CPFd3tF5S"
      },
      "source": [
        "We can analyze how much global memory accesses we reduce by leveraging shared memory:\n",
        "\n",
        "* There are $M \\times K$ elements in $A$ and $N \\times K$ elements in $B$.\n",
        "When not using shared memory, each element of $A$ is read for $N$ times,\n",
        "and each element of $B$ is read for $M$ times.\n",
        "So number of accesses to $A$ and $B$ in global memory are both $MNK$.\n",
        "* With shared memory tiling, the number of times each element of $A$ is read becomes $\\frac{N}{\\mathrm{tile}_y}$,\n",
        "and the number of times each element of $B$ is read becomes $\\frac{M}{\\mathrm{tile}_x}$.\n",
        "And the total number of accesses to $A$ and $B$ are divided by $\\mathrm{tile}_y$ and $\\mathrm{tile}_x$ respectively.\n"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "RERemneytF5S"
      },
      "source": [
        "You need to implement the shared memory tiling in the `shared_memory_tiling` function in `gemm_relu_add.py`.\n",
        "Below are the schedule primitives you will use in this task.\n",
        "We provide [another Jupyter notebook](https://github.com/mlsyscourse/assignment2/blob/main/schedule_example.ipynb) that walks you through an example\n",
        "of using some of these schedule primitives for your reference.\n",
        "Meanwhile, you can click the links below to check out their documentations,\n",
        "which contain a basic example on how to use the primitive.\n",
        "We also provide instructions in your TODO area in `gemm_relu_add.py`.\n",
        "\n",
        "- `split` [(docs)](https://tvm.apache.org/docs/reference/api/python/tir/schedule.html#tvm.tir.schedule.Schedule.split)\n",
        "  - It splits one loop into multiple loops that collectively iterate the iteration space of the original loop.\n",
        "  We use `split` for tiling.\n",
        "- `reorder` [(docs)](https://tvm.apache.org/docs/reference/api/python/tir/schedule.html#tvm.tir.schedule.Schedule.reorder)\n",
        "  - It reorders the specified contiguous loops into a new order.\n",
        "  We apply `reorder` for loops after splitting for tiling.\n",
        "- `bind` [(docs)](https://tvm.apache.org/docs/reference/api/python/tir/schedule.html#tvm.tir.schedule.Schedule.bind)\n",
        "  - It binds a loop to `blockIdx.x/y/z` or `threadIdx.x/y/z` on GPU,\n",
        "  so that we can specify the area to compute of a thread block or a single thread.\n",
        "- `cache_read` [(docs)](https://tvm.apache.org/docs/reference/api/python/tir/schedule.html#tvm.tir.schedule.Schedule.cache_read)\n",
        "  - It generates a cache stage for the specified region in the specified memory scope.\n",
        "  We use `cache_read` to generate the read stages from global memory to shared memory.\n",
        "- `compute_at` [(docs)](https://tvm.apache.org/docs/reference/api/python/tir/schedule.html#tvm.tir.schedule.Schedule.compute_at)\n",
        "  - It moves a computation (e.g., the shared memory read stage) to the location under the specified loop.\n",
        "  We use `compute_at` to move the shared memory read stages to the right location.\n",
        "\n",
        "You can run `gemm_relu_add.py` to see how the function looks like after your optimization.\n",
        "Note: you can insert `sch.show()` at any position to print out the function,\n",
        "so that you can visually see how the function looks like."
      ]
    },
    {
      "cell_type": "code",
      "execution_count": 9,
      "metadata": {
        "id": "fnVKiVNstF5S",
        "outputId": "0f769663-ebdc-47f7-b08b-8c634d81ded4",
        "colab": {
          "base_uri": "https://localhost:8080/"
        }
      },
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            "Traceback (most recent call last):\n",
            "  File \"/content/drive/MyDrive/15442/assignment2/gemm_relu_add.py\", line 303, in <module>\n",
            "    sch = manual_schedule()\n",
            "          ^^^^^^^^^^^^^^^^^\n",
            "  File \"/content/drive/MyDrive/15442/assignment2/gemm_relu_add.py\", line 65, in manual_schedule\n",
            "    A_shared, B_shared = shared_memory_tiling(sch, tile_x, tile_y, tile_k)\n",
            "                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n",
            "  File \"/content/drive/MyDrive/15442/assignment2/gemm_relu_add.py\", line 156, in shared_memory_tiling\n",
            "    return A_shared, B_shared\n",
            "                     ^^^^^^^^\n",
            "NameError: name 'B_shared' is not defined. Did you mean: 'A_shared'?\n"
          ]
        }
      ],
      "source": [
        "!python3 gemm_relu_add.py"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "n2itGiCatF5S"
      },
      "source": [
        "### Task 2. Register tiling (20 pt)\n",
        "\n",
        "In the previous subsection, we focus on handling the `matmul` region that **a thread block collectively computes**.\n",
        "In this subsection, we dive deeper to figure out the `matmul` region that **a single thread computes**.\n",
        "\n",
        "The idea is pretty much similar to the shared memory tiling.\n",
        "We can also let a single thread compute a tile in `matmul`.\n",
        "For example, we assign each thread in a thread block to compute a tile of size `(thread_tile_x, thread_tile_y)`.\n",
        "And moreover, rather than directly load `A` and `B` from shared memory when computing the tile,\n",
        "we again first load `A` and `B` from shared memory to **local registers**.\n",
        "Registers are local memory in a running CUDA thread that is running,\n",
        "and can be accessed in much shorter time than shared memory.\n",
        "Similarly, we also need to do thread-level tiling along the `K` dimension,\n",
        "because each thread has very limited number of available registers.\n",
        "And our goal is to make sure the data that we want to load from `A` and `B` in each thread-level tile can fit into the registers.\n",
        "With register tiling, we use $(\\mathrm{thread\\_tile}_x + \\mathrm{thread\\_tile}_y) \\times \\mathrm{thread\\_tile}_k$\n",
        "registers for reading data from the shared memory of `A` and `B` in total.\n",
        "\n",
        "\n",
        "<img src=\"https://raw.githubusercontent.com/mlsyscourse/assignment2/main/figure/register-tiling.jpg\" alt=\"figure/register-tiling.jpg\" width=\"50%\">\n"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "8Ir3640wtF5S"
      },
      "source": [
        "\n",
        "It worths noting that, by fixing the thread tile size, we equivalently fixed the number\n",
        "of threads in each thread block:\n",
        "a thread block computes a tile of `(tile_x, tile_y)`, and a single thread computes a tile of\n",
        "`(thread_tile_x, thread_tile_y)`.\n",
        "So in a thread block, `blockDim.x` is `tile_x / thread_tile_x`, `blockDim.y` is `tile_y / thread_tile_y`,\n",
        "and the total number of threads in a thread block is `(tile_x / thread_tile_x) * (tile_y / thread_tile_y)`.\n"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "Ii866W60tF5S"
      },
      "source": [
        "You need to implement the register tiling in the `register_tiling` function in `gemm_relu_add.py`.\n",
        "As mentioned above, your implementation of register tiling should follow the same pattern and steps\n",
        "as your implementation of shared memory tiling.\n",
        "So make sure you understand each step of the shared memory tiling before starting this task.\n",
        "The schedule primitives you will use in this task is the same as task 1.\n",
        "And please note that for register tiling, you should use `\"local\"` (which means local registers)\n",
        "as the scope of `cache_read`, rather than `\"shared\"` which you used in task 1."
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "iaYvZV3gtF5S"
      },
      "outputs": [],
      "source": [
        "!python3 gemm_relu_add.py"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "KdqzuYPctF5S"
      },
      "source": [
        "### Task 3. Cooperative fetching (20 pt)\n",
        "\n",
        "Throughout the shared memory tiling and register tiling,\n",
        "we have assigned each thread a `matmul` region to compute.\n",
        "This concludes our arrangement of the GeMM computation.\n",
        "Nevertheless, we still have a few more optimization steps till the end.\n",
        "The first one is **cooperative fetching**, where we optimize the memory load\n",
        "from global memory to shared memory for both `A` and `B`.\n",
        "\n",
        "Remember in the \"shared memory tiling\" subsection, we created stages for\n",
        "a thread block to read data from `A` and `B` into their respective shared memory.\n",
        "However, you may notice that how the the data is read remains unspecified.\n",
        "Specifically, we have known which `A`/`B` region a thread block should read,\n",
        "but **do not specify which `A`/`B` elements a single thread should read**.\n",
        "If we do not specify this, by default *every* thread in a thread block will\n",
        "read the entire `A`/`B` regions that this thread block is responsible for and\n",
        "write the values into shared memory correspondingly.\n",
        "Since the shared memory of a thread block is accessible to all threads,\n",
        "this default behavior, as a result, leads to duplicate global memory reads\n",
        "and shared memory writes, and fails to reduce the number of global memory accesses.\n",
        "\n",
        "This motivates us to implement cooperative fetching.\n",
        "Cooperative fetching means all the threads in a thread block\n",
        "collectively (\"*cooperative*\") load values from global memory to shared memory (\"*fetching*\").\n",
        "To make sure each element in the tile is read only once (by some thread),\n",
        "we can divide the number of elements in the shared memory tile evenly by\n",
        "the number of threads, yielding the number of elements each thread loads.\n",
        "Then, we let all the threads in the thread block to load values in memory order.\n",
        "\n",
        "For our example, we can calculate that each thread in a thread block needs to\n",
        "load `thread_tile_x * thread_tile_y * tile_k / tile_y` elements from `A`,\n",
        "and likewise, `thread_tile_x * thread_tile_y * tile_k / tile_x` elements from `B`.\n",
        "If we denote the number of total threads (`(tile_x / thread_tile_x) * (tile_y / thread_tile_y)`) as\n",
        "`num_threads`, then when loading an `A` tile to shared memory, in the first round all the threads\n",
        "load the first continuous `num_threads` elements, in the second round they load\n",
        "the next continuous `num_threads` elements, and keep loading for\n",
        "`thread_tile_x * thread_tile_y * tile_k / tile_y` times.\n",
        "This applies to the shared memory load of `B` in the same way.\n",
        "\n",
        "[The other Jupyter notebook](https://github.com/mlsyscourse/assignment2/blob/main/schedule_example.ipynb) contains a simple example of\n",
        "cooperative fetching that you might find helpful for understanding,\n",
        "if you have not went through it."
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "m8L8Jz9NtF5S"
      },
      "source": [
        "You need to implement the cooperative fetching in the `cooperative_fetching` function in `gemm_relu_add.py`.\n",
        "As you can see in the code, since the cooperative fetching for `A` and `B` are the same,\n",
        "we can write a common schedule function and apply it to the shared memory read stages\n",
        "of both `A` and `B`.\n",
        "The new schedule primitive you will use in this task is\n",
        "`fuse` [(docs)](https://tvm.apache.org/docs/reference/api/python/tir/schedule.html#tvm.tir.schedule.Schedule.fuse),\n",
        "which, on the contrary to `split`, fuses multiple loops into a single loop."
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "dqLU7atOtF5S"
      },
      "outputs": [],
      "source": [
        "!python3 gemm_relu_add.py"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "cEoBdr0vtF5T"
      },
      "source": [
        "### Task 4. Write Cache (10 pt)\n",
        "\n",
        "We can now move on to the stage of writing the GeMM computation result into `matmul`.\n",
        "So far, our GeMM computation still directly writes the results into the global memory of `matmul`,\n",
        "with each location of `matmul` written for `K` times, as our GeMM takes the summation over the `K` dimension.\n",
        "This is obviously not optimal.\n",
        "\n",
        "Instead of writing the computation results directly into global memory,\n",
        "we can accumulate the summation in local registers,\n",
        "and write the result into global memory for fewer times after the accumulation is finished."
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "KuZXK6lntF5T"
      },
      "source": [
        "You need to implement the write cache in the `write_cache` function in `gemm_relu_add.py`.\n",
        "In this task, you will use the schedule primitive\n",
        "`cache_write` [(docs)](https://tvm.apache.org/docs/reference/api/python/tir/schedule.html#tvm.tir.schedule.Schedule.cache_write)\n",
        "and\n",
        "`reverse_compute_at` [(docs)](https://tvm.apache.org/docs/reference/api/python/tir/schedule.html#tvm.tir.schedule.Schedule.reverse_compute_at)\n",
        "to put the write cache stage at the right location.\n",
        "Similar to `cache_read` which generates a read cache stage for a computation,\n",
        "`cache_write` generates a write cache stage for a computation at the specified scope.\n",
        "`reverse_compute_at` works in basically the same way as `compute_at`,\n",
        "with the difference being `compute_at` moves a computation **in front of** the target loop into the target loop,\n",
        "while `reverse_compute_at` moves a computation **behind** the target loop into the target loop."
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "8ZEaRiH2tF5T"
      },
      "outputs": [],
      "source": [
        "!python3 gemm_relu_add.py"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "XvaEAdYytF5T"
      },
      "source": [
        "### Task 5. Epilogue Fusion (10 pt)\n",
        "\n",
        "The subsections above include the common techniques people use\n",
        "to optimize a GeMM workload.\n",
        "Now we can take care of the ReLU and add operators.\n",
        "Though these two operators are computation-wise much more lightweight\n",
        "compared to the GeMM,\n",
        "right now they still account for a quite amount of time,\n",
        "since they need to read/write directly from/to global memory.\n",
        "This can be optimized by inlining the lightweight epilogue operators\n",
        "into the write-back stage of the scheduled GeMM workload,\n",
        "where the result of GeMM is still in registers.\n",
        "This optimizes the redundant memory accesses.\n"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "EDszFnt0tF5T"
      },
      "source": [
        "You need to implement the epilogue fusion in the `epilogue_fusion` function in `gemm_relu_add.py`,\n",
        "where you will use `get_block` to retrieve the computation of addition and ReLU,\n",
        "and use `reverse_compute_inline` [(docs)](https://tvm.apache.org/docs/reference/api/python/tir/schedule.html#tvm.tir.schedule.Schedule.reverse_compute_inline)\n",
        "to inline the addition and ReLU into the write-back stage of GeMM."
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "pSFGWJpNtF5T"
      },
      "outputs": [],
      "source": [
        "!python3 gemm_relu_add.py"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "7JO2VHi8tF5T"
      },
      "source": [
        "---"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "MEYfeExXtF5T"
      },
      "source": [
        "### If you are using Google Colab...\n",
        "\n",
        "Now we need to switch to GPU runtime and install the PyPI package with CUDA support before\n",
        "running tests.\n",
        "Please go to \"Runtime - Change runtime type\" in the navigation bar, and select \"T4 GPU\".\n",
        "Then run the cells below to install the PyPI package, verify the installation,\n",
        "and mount the Google Drive again.\n",
        "\n",
        "**Note 1.** Be sure to change runtime type to use T4 GPU.\n",
        "Or otherwise you will see library error when importing TVM in Python below.\n",
        "\n",
        "**Note 2.** Please disconnect the GPU runtime when you are not using it.\n",
        "Otherwise you may hit the Colab GPU usage limit and will be temporarily not able to\n",
        "connect to a GPU in Colab if you are a free Colab user."
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "Wm_I8jxKtF5T"
      },
      "outputs": [],
      "source": [
        "!python3 -m pip install mlc-ai-cu123 -f https://mlc.ai/wheels"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "NSYy43iotF5T"
      },
      "outputs": [],
      "source": [
        "import tvm\n",
        "tvm.__path__"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "_UbWDrjWtF5T"
      },
      "outputs": [],
      "source": [
        "# Code to set up the assignment\n",
        "from google.colab import drive\n",
        "drive.mount('/content/drive')\n",
        "%cd /content/drive/MyDrive/15442/assignment2"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "0DymULHqtF5Y"
      },
      "source": [
        "---"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "KSGyqgBatF5Y"
      },
      "source": [
        "Now that you have finished implementing all the optimizations,\n",
        "you can test the numerical correctness of your code via running the following."
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "M5l2_EWwtF5Y",
        "outputId": "f9e8bfea-d3f8-4fcf-eef6-7ef39e5ca4d2"
      },
      "outputs": [
        {
          "name": "stdout",
          "output_type": "stream",
          "text": [
            "Passing test round 0...\n",
            "Passing test round 1...\n",
            "Passing test round 2...\n",
            "Passing test round 3...\n",
            "Passing test round 4...\n",
            "Passed all tests.\n"
          ]
        }
      ],
      "source": [
        "!python3 evaluate.py --test"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "pqVDi3jttF5Y"
      },
      "source": [
        "You can evaluate the execution time of function after your optimization via running the following:"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "5i5z2j6XtF5Z"
      },
      "outputs": [],
      "source": [
        "!python3 evaluate.py --evaluate-manual"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "JgM-ZgL1tF5Z"
      },
      "source": [
        "To help you get a sense of how much performance your optimization gains,\n",
        "we can evaluate a naive GeMM + ReLU + add function with little optimizations.\n",
        "Ideally, you should find that your optimization is times faster than the naive optimization."
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "gNp0fqqXtF5Z"
      },
      "outputs": [],
      "source": [
        "!python3 evaluate.py --evaluate-naive"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "iUTplRPxtF5Z"
      },
      "source": [
        "You can print out the CUDA source code of your scheduled workload that TVM generates,\n",
        "and compare it with the Python script you printed\n",
        "via `sch.show()`.\n",
        "As a practice, try to point out which parts in the CUDA source code\n",
        "are the shared memory, local registers,\n",
        "the main GeMM computation, cooperative fetching, write cache,\n",
        "and the fused epilogue respectively."
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "spVLHw7btF5Z"
      },
      "outputs": [],
      "source": [
        "!python3 evaluate.py --show-cuda"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "E9rr2wt3tF5Z"
      },
      "source": [
        "## Part 2. Auto Tuning (20 pt)\n",
        "\n",
        "In this part, you have the chance to step further and apply automatic tuning to\n",
        "our GeMM + ReLU + add workload with some adaptation to your code in part 1,\n",
        "so that the optimized workload can run even faster on GPU.\n",
        "\n",
        "In the previous part, we only implemented one schedule for the workload.\n",
        "However, there are many other ways to schedule and optimize the workload,\n",
        "and the particular schedule in part 1 may not be optimal on GPU.\n",
        "A typical example is the tile size:\n",
        "you can easily get other schedules by tweaking the\n",
        "tile sizes for shared memory tiling and register tiling.\n",
        "\n",
        "To describe the problem we want to tackle with auto tuning --\n",
        "all the possible choices of schedules form a search space,\n",
        "and each schedule choice has a corresponding execution time on GPU.\n",
        "We want to find out the schedule with the shortest execution time.\n",
        "\n",
        "However, the execution time of a schedule is hard to be predictable,\n",
        "especially for complicated workloads such as GeMM and convolution\n",
        "(which we don't cover in this assignment).\n",
        "This is because the execution time of a scheduled program on GPU\n",
        "usually depends on multiple factors, making it challenging to build up\n",
        "analytical model to find the best performant schedule.\n",
        "This motivates us to build auto tuning tools to help find the\n",
        "best schedule within the search space on the target GPU.\n",
        "\n",
        "The problem of auto tuning generally consists of two sub-problems.\n",
        "The first one is to generate the search space (i.e., describing the\n",
        "set of programs/schedules in the search space). And the other one\n",
        "is to find the best performant schedule in the space."
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "cxF1dVUbtF5Z"
      },
      "source": [
        "---"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "IJ_cZEtttF5Z"
      },
      "source": [
        "Your task in this part is to define the search space for our\n",
        "GeMM + ReLU + add workload in the function `auto_tuning_schedule` of `auto_tuning.py`.\n",
        "To make things easier, you can only focus on the different\n",
        "choices of tile size in this assignment, and ideally your implementation of\n",
        "the `auto_tuning_schedule` function is adapted from your code in part 1.\n",
        "\n",
        "Obviously, the most straightforward choice is to directly reuse the schedule in part 1.\n",
        "Doing this gives us a search space which only contains a single schedule.\n",
        "You can also manually adjust the tile sizes to check if different tile sizes\n",
        "offer better performance.\n",
        "\n",
        "If you want to define a search space that goes beyond a single schedule,\n",
        "the primitive [`Schedule.sample_perfect_tile`](https://tvm.apache.org/docs/reference/api/python/tir/schedule.html#tvm.tir.schedule.Schedule.sample_perfect_tile)\n",
        "in `tir.Schedule` helps you to sample the tile sizes from the specified loop.\n",
        "For example, for a given schedule `sch`, a given loop `i` with loop length `length`,\n",
        "```python\n",
        "tile0, tile1, tile2, tile3 = sch.sample_perfect_tile(i, n=4)\n",
        "```\n",
        "returns four integer tile sizes `[tile0, tile1, tile2, tile3]` in a list,\n",
        "such that `tile0 * tile1 * tile2 * tile3 == length`.\n",
        "And you can thereby use these tile sizes in schedule primitives such as\n",
        "`split`:\n",
        "```python\n",
        "i0, i1, i2, i3 = sch.split(i, factors=[tile0, tile1, tile2, tile3])\n",
        "```\n",
        "\n",
        "Now, go ahead and implement function `auto_tuning_schedule`.\n",
        "We do not provide other examples for you in this part.\n",
        "\n",
        "**Note:** if you feel unsure about this part and don't know how to start,\n",
        "just try to copy and paste your part 1 code into this function,\n",
        "proceed and run the auto tuning code below to see if it is runnable\n",
        "and gives you an execution time. Then you can come back to update your\n",
        "`auto_tuning_schedule` implementation.\n",
        "This may help you build confidence.\n"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "MGRnlMa_tF5Z"
      },
      "source": [
        "---"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "CLLGqDcqtF5Z"
      },
      "source": [
        "After defining the search space, let's take a look at the second\n",
        "sub-problem on how to find the best performance schedule within the search space.\n",
        "\n",
        "The most basic way of auto tuning is simply iterate over the entire search space,\n",
        "and evaluate the performance on GPU for every schedule in the space.\n",
        "As you can imagine, this is effective and straightforward when the\n",
        "search space is not too large. However, it is time-consuming\n",
        "to go through every single choice when the search space is large.\n",
        "\n",
        "Here we use an improved way based on genetic algorithms,\n",
        "so that we do not have to go through the entire search space.\n",
        "We will not expand on the details here.\n",
        "If you are interested, you can refer to the papers of\n",
        "[AutoTVM](https://proceedings.neurips.cc/paper_files/paper/2018/file/8b5700012be65c9da25f49408d959ca0-Paper.pdf)\n",
        "and [Meta Schedule](https://proceedings.neurips.cc/paper_files/paper/2022/file/e894eafae43e68b4c8dfdacf742bcbf3-Paper-Conference.pdf)\n",
        "for more details.\n",
        "\n",
        "You can run the cell below to automatically tune the workload\n",
        "with the search space you defined.\n",
        "**The full auto tuning under the default settings may take at most 5 minutes on Google Colab if you use `sample_perfect_tile`.**"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "WGwJfnpbtF5Z"
      },
      "outputs": [],
      "source": [
        "!python3 auto_tuning.py"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "Lg17l8v-tF5Z"
      },
      "source": [
        "After tuning, you are expected to see the table\n",
        "```\n",
        " ID | Name |        FLOP | Weight | Speed (GFLOPS) | Latency (us) | Weighted Latency (us) | Trials | Done\n",
        "----------------------------------------------------------------------------------------------------------\n",
        "  0 | main | 17188257792 |      1 |     xxxxxxxxxx |   xxxxxxxxxx |            xxxxxxxxxx |    xxx |    Y\n",
        "----------------------------------------------------------------------------------------------------------\n",
        "```\n",
        "in the end, and a function `apply_trace` printed out:\n",
        "```python\n",
        "# from tvm import tir\n",
        "def apply_trace(sch: tir.Schedule) -> None:\n",
        "  b0 = sch.get_block(name=\"gemm\", func_name=\"main\")\n",
        "  # ...\n",
        "```\n",
        "\n",
        "Please, **copy the entire `apply_trace` function, and paste it into `trace_submission.py`**.\n",
        "`trace_submission.py` is the only file you will submit for this part."
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "QiUw7c4ZtF5Z"
      },
      "source": [
        "The column \"Latency\" in the table shows the execution time you get after auto tuning.\n",
        "**When grading, we will manually run the command in the cell below to measure the execution time of the schedule in `trace_submission.py` on Google Colab with NVIDIA T4 GPU.**\n",
        "You can also run the cell below to check the execution time.\n",
        "The time it shows might be slightly longer than the latency shown in the table due to variance,\n",
        "which is normal."
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "wAhidZG5tF5Z"
      },
      "outputs": [],
      "source": [
        "!python3 evaluate.py --evaluate-tuned"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "ayG7ISAftF5a"
      },
      "source": [
        "The scores you will get is based on the execution time you can reach.\n",
        "Here is the score table for your reference:\n",
        "\n",
        "| Execution time after tuning (ms) | Scores (pt) |\n",
        "| -: | :-: |\n",
        "| ≤ 20.00 | 20 |\n",
        "| ≤ 40.00 | 15 |\n",
        "| ≤ 80.00 | 10 |\n",
        "| ≤ 160.00 | 5  |"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "qyJs3lACtF5a"
      },
      "source": [
        "## Part 3. Assignment Feedback (0 pt)\n",
        "\n",
        "This is the second time we offer this course, and we appreciate any assignment feedback from you.\n",
        "You can leave your feedback (if any) in `feedback.txt`, and submit it together with the source code.\n",
        "Possible choices can be:\n",
        "\n",
        "- Are the notebooks and instructions clear enough?\n",
        "- How difficult do you think this assignment is?\n",
        "- How much time does the assignment take? Which task takes the most time?\n",
        "- Which part of the assignment do you feel hard to understand?\n",
        "- And any other things you would like to share.\n",
        "\n",
        "Your feedback will be very useful in helping us improve the assignment quality\n",
        "for next years.\n"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "5h-vA6CVtF5a"
      },
      "source": [
        "## Code Submission and Grading\n",
        "\n",
        "In the home directory for the assignment, execute the command"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "e343m9dhtF5a"
      },
      "outputs": [],
      "source": [
        "!zip handin.zip gemm_relu_add.py trace_submission.py feedback.txt"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "xbXXW6IEtF5a"
      },
      "source": [
        "This will create a zip file with `gemm_relu_add.py`, `trace_submission.py` and `feedback.txt`.\n",
        "You can check the contents of `handin.zip` to make sure it contains all the needed files:"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "KNS3DEX2tF5a"
      },
      "outputs": [],
      "source": [
        "!zipinfo -1 handin.zip"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "pw9EXuuVtF5a"
      },
      "source": [
        "It is expected to list the three files:\n",
        "```\n",
        "gemm_relu_add.py\n",
        "trace_submission.py\n",
        "feedback.txt\n",
        "```\n",
        "\n",
        "Then, please go to GradeScope at https://www.gradescope.com/courses/951055 and submit the file `handin.zip` to Assignment 2.\n",
        "\n",
        "The assignment will be automatically graded.\n",
        "* For both parts, the autograder checks both the optimization completeness and the numerical correctness. You will not get full scores if the autograder finds your optimization schedule is numerically incorrect.\n",
        "* For `gemm_relu_add.py`, please make sure NOT to change the signatures of `shared_memory_tiling`, `register_tiling`, `cooperative_fetching`, `write_cache` and `epilogue_fusion`, or otherwise the autograder may not process your submission properly.\n",
        "* Please make sure that your submitted `gemm_relu_add.py` and `trace_submission.py` are placed at the root level of the zip file (i.e., they are not in any sub-folder),\n",
        "or **otherwise the autograder may not process your submission properly**.\n",
        "* You can submit multiple times, and the time stamp of the last submission will be used in determining any late penalties.\n",
        "\n",
        "**Any attempt to manipulate or compromise the integrity of the autograder will result in severe penalties.**\n",
        "\n",
        "If you are enrolled in the course (on SIO), but not registered on GradeScope, please let the course staff know in a private post on Piazza.\n"
      ]
    }
  ],
  "metadata": {
    "kernelspec": {
      "display_name": "Python 3",
      "language": "python",
      "name": "python3"
    },
    "language_info": {
      "codemirror_mode": {
        "name": "ipython",
        "version": 3
      },
      "file_extension": ".py",
      "mimetype": "text/x-python",
      "name": "python",
      "nbconvert_exporter": "python",
      "pygments_lexer": "ipython3",
      "version": "3.10.8"
    },
    "colab": {
      "provenance": []
    }
  },
  "nbformat": 4,
  "nbformat_minor": 0
}