if (utils.scm_checkout()) return

withCredentials([string(
    credentialsId: 'jwst-codecov',
    variable: 'codecov_token')]) {

env_vars = [
    "CRDS_SERVER_URL=https://jwst-crds.stsci.edu",
    "CRDS_PATH=./crds_cache",
    "CRDS_CLIENT_RETRY_COUNT=3",
    "CRDS_CLIENT_RETRY_DELAY_SECONDS=20",
]

// pip related setup for local index, not used currently
def pip_index = "https://bytesalad.stsci.edu/artifactory/api/pypi/datb-pypi-virtual/simple"
def pip_install_args = "--index-url ${pip_index} --progress-bar=off"


// Generate distributions build
bc0 = new BuildConfig()
bc0.nodetype = 'linux'
bc0.name = 'build-dists'
bc0.conda_ver = '4.8.2'
bc0.conda_packages = [
    "python",
]
bc0.build_cmds = [
    "pip install pep517",
    "python -m pep517.build .",
]

// Generate pip build/test with released upstream dependencies
bc1 = utils.copy(bc0)
bc1.name = "stable-deps"
bc1.env_vars = env_vars
bc1.build_cmds = [
    "pip install -e .[test]",
]
bc1.test_cmds = [
    "pytest -r sxf --junitxml=results.xml",
]

// Generate conda-free build with python 3.7
bc2 = new BuildConfig()
bc2.nodetype = 'python3.7'
bc2.name = 'conda-free'
bc2.env_vars = env_vars
bc2.build_cmds = [
    "pip install -e .[test]",
]
bc2.test_cmds = [
    "pytest -r sxf --junitxml=results.xml"
]


// Audit code with bandit
bc3 = new BuildConfig()
bc3.nodetype = 'python3.7'
bc3.name = 'security-audit'
bc3.build_cmds = [
    "pip install -e .[test] bandit",
]
bc3.test_cmds = [
    "bandit --exclude 'jwst/*test*' -r jwst scripts",
]

utils.run([bc0, bc1, bc2, bc3])
}  // withCredentials
