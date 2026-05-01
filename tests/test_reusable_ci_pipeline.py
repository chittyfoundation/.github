"""
Tests for .github/workflows/reusable-ci-pipeline.yml

This PR fixed deeply-compounding YAML indentation that made all keys
incorrectly nested. These tests verify:
  - The YAML is valid and parses correctly
  - Inputs, secrets, and jobs are at the correct nesting levels
  - All input defaults and types are correct
  - Job dependencies, conditions, and step logic are correct
  - The language-detection shell script handles all file combinations
"""

import os
import subprocess
import tempfile
import pytest
import yaml

WORKFLOW_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    ".github",
    "workflows",
    "reusable-ci-pipeline.yml",
)


@pytest.fixture(scope="module")
def workflow():
    """
    Load the GitHub Actions workflow YAML and return its parsed content.
    
    Returns:
        dict: Mapping representing the workflow YAML document as parsed by PyYAML.
    """
    with open(WORKFLOW_PATH) as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# YAML validity and top-level structure
# ---------------------------------------------------------------------------


class TestYamlValidity:
    def test_yaml_parses_without_error(self):
        """The fixed indentation must produce valid YAML."""
        with open(WORKFLOW_PATH) as f:
            doc = yaml.safe_load(f)
        assert doc is not None

    def test_top_level_keys_present(self, workflow):
        # PyYAML parses YAML 1.1 "on" as boolean True
        assert True in workflow  # the "on:" trigger key
        assert "jobs" in workflow
        assert "name" in workflow

    def test_workflow_name(self, workflow):
        assert workflow["name"] == "Reusable CI Pipeline"

    def test_trigger_is_workflow_call(self, workflow):
        # PyYAML parses "on:" as boolean True due to YAML 1.1 rules
        assert "workflow_call" in workflow[True]

    def test_inputs_at_correct_nesting_level(self, workflow):
        """After the fix, inputs must be a direct child of workflow_call, not
        buried deeper due to compounding indentation."""
        wc = workflow[True]["workflow_call"]
        assert "inputs" in wc, "inputs must be a direct child of workflow_call"

    def test_secrets_at_correct_nesting_level(self, workflow):
        """After the fix, secrets must be a peer of inputs under workflow_call,
        not nested inside inputs."""
        wc = workflow[True]["workflow_call"]
        assert "secrets" in wc, "secrets must be a peer of inputs under workflow_call"
        # Confirm secrets is NOT inside inputs
        assert "secrets" not in wc.get("inputs", {}), (
            "secrets must not be nested inside inputs"
        )

    def test_jobs_at_top_level(self, workflow):
        """jobs must be a top-level key, not nested inside on.workflow_call."""
        assert isinstance(workflow["jobs"], dict)
        wc = workflow[True]["workflow_call"]
        assert "jobs" not in wc, "jobs must be a top-level key, not inside workflow_call"


# ---------------------------------------------------------------------------
# Input parameters
# ---------------------------------------------------------------------------


class TestInputs:
    @pytest.fixture
    def inputs(self, workflow):
        """
        Retrieve the `inputs` mapping under `workflow_call` from a parsed workflow document.
        
        Parameters:
            workflow (dict): The YAML-parsed workflow mapping (as returned by `yaml.safe_load`),
                where the top-level `on` key may be represented as the boolean `True` by PyYAML.
        
        Returns:
            dict: Mapping of input names to their input definitions found at
                `workflow[True]['workflow_call']['inputs']`.
        """
        return workflow[True]["workflow_call"]["inputs"]

    def test_all_inputs_present(self, inputs):
        expected = {
            "node-version",
            "python-version",
            "run-tests",
            "run-lint",
            "run-security",
            "run-ai-review",
            "working-directory",
        }
        assert set(inputs.keys()) == expected

    def test_node_version_default(self, inputs):
        assert inputs["node-version"]["default"] == "20"

    def test_node_version_type(self, inputs):
        assert inputs["node-version"]["type"] == "string"

    def test_node_version_not_required(self, inputs):
        assert inputs["node-version"]["required"] is False

    def test_python_version_default(self, inputs):
        assert inputs["python-version"]["default"] == "3.11"

    def test_python_version_type(self, inputs):
        assert inputs["python-version"]["type"] == "string"

    def test_run_tests_default_true(self, inputs):
        assert inputs["run-tests"]["default"] is True

    def test_run_tests_type_boolean(self, inputs):
        assert inputs["run-tests"]["type"] == "boolean"

    def test_run_lint_default_true(self, inputs):
        assert inputs["run-lint"]["default"] is True

    def test_run_lint_type_boolean(self, inputs):
        assert inputs["run-lint"]["type"] == "boolean"

    def test_run_security_default_true(self, inputs):
        assert inputs["run-security"]["default"] is True

    def test_run_security_type_boolean(self, inputs):
        assert inputs["run-security"]["type"] == "boolean"

    def test_run_ai_review_default_false(self, inputs):
        """AI review should be opt-in (default false)."""
        assert inputs["run-ai-review"]["default"] is False

    def test_run_ai_review_type_boolean(self, inputs):
        assert inputs["run-ai-review"]["type"] == "boolean"

    def test_working_directory_default_dot(self, inputs):
        assert inputs["working-directory"]["default"] == "."

    def test_working_directory_type_string(self, inputs):
        """
        Verify that the `working-directory` workflow input is declared with type "string".
        
        Asserts that the `working-directory` entry in the `inputs` mapping has its `type` set to `"string"`.
        """
        assert inputs["working-directory"]["type"] == "string"

    def test_all_inputs_not_required(self, inputs):
        for name, config in inputs.items():
            assert config.get("required") is False, (
                f"Input '{name}' should not be required"
            )

    def test_no_extra_keys_inside_inputs(self, inputs):
        """
        Assert that the workflow_call `inputs` mapping does not contain the keys "secrets" or "jobs".
        """
        assert "secrets" not in inputs
        assert "jobs" not in inputs


# ---------------------------------------------------------------------------
# Secrets
# ---------------------------------------------------------------------------


class TestSecrets:
    @pytest.fixture
    def secrets(self, workflow):
        """
        Retrieve the `secrets` mapping declared under the workflow's `workflow_call` trigger.
        
        Parameters:
            workflow (dict): Parsed YAML document for the workflow (the object returned by `yaml.safe_load`).
        
        Returns:
            dict: Mapping of secret names to their schema objects as declared under `workflow_call.secrets`.
        """
        return workflow[True]["workflow_call"]["secrets"]

    def test_anthropic_api_key_present(self, secrets):
        """
        Asserts the workflow_call defines an ANTHROPIC_API_KEY secret.
        
        Verifies that the parsed workflow's `workflow_call.secrets` mapping contains the key "ANTHROPIC_API_KEY".
        """
        assert "ANTHROPIC_API_KEY" in secrets

    def test_anthropic_api_key_not_required(self, secrets):
        assert secrets["ANTHROPIC_API_KEY"]["required"] is False

    def test_snyk_token_present(self, secrets):
        assert "SNYK_TOKEN" in secrets

    def test_snyk_token_not_required(self, secrets):
        assert secrets["SNYK_TOKEN"]["required"] is False

    def test_exactly_two_secrets(self, secrets):
        assert set(secrets.keys()) == {"ANTHROPIC_API_KEY", "SNYK_TOKEN"}


# ---------------------------------------------------------------------------
# Jobs presence and names
# ---------------------------------------------------------------------------


class TestJobs:
    @pytest.fixture
    def jobs(self, workflow):
        """
        Retrieve the top-level `jobs` mapping from a parsed GitHub Actions workflow document.
        
        Parameters:
            workflow (dict): Parsed workflow YAML as returned by `yaml.safe_load`.
        
        Returns:
            dict: Mapping of job IDs to their job definitions (the workflow's top-level `jobs` section).
        """
        return workflow["jobs"]

    def test_all_jobs_present(self, jobs):
        """
        Assert the workflow defines exactly the expected top-level job IDs.
        
        Parameters:
            jobs (dict): Mapping of job identifiers to job definitions loaded from the workflow YAML.
        """
        assert set(jobs.keys()) == {"detect", "lint", "test", "security", "ai-review"}

    def test_detect_job_name(self, jobs):
        assert jobs["detect"]["name"] == "Detect Language"

    def test_lint_job_name(self, jobs):
        assert jobs["lint"]["name"] == "Lint"

    def test_test_job_name(self, jobs):
        assert jobs["test"]["name"] == "Test"

    def test_security_job_name(self, jobs):
        assert jobs["security"]["name"] == "Security Scan"

    def test_ai_review_job_name(self, jobs):
        assert jobs["ai-review"]["name"] == "AI Review"

    def test_all_jobs_run_on_ubuntu(self, jobs):
        for job_id, job in jobs.items():
            assert job.get("runs-on") == "ubuntu-latest", (
                f"Job '{job_id}' should run on ubuntu-latest"
            )


# ---------------------------------------------------------------------------
# detect job
# ---------------------------------------------------------------------------


class TestDetectJob:
    @pytest.fixture
    def detect(self, workflow):
        """
        Return the top-level 'detect' job mapping from a parsed workflow document.
        
        Parameters:
            workflow (dict): Parsed YAML workflow mapping (as returned by yaml.safe_load).
        
        Returns:
            dict: Mapping describing the 'detect' job (workflow["jobs"]["detect"]).
        """
        return workflow["jobs"]["detect"]

    def test_no_needs_dependency(self, detect):
        assert "needs" not in detect

    def test_outputs_language(self, detect):
        assert "outputs" in detect
        assert "language" in detect["outputs"]

    def test_language_output_references_detect_step(self, detect):
        output_val = detect["outputs"]["language"]
        assert "steps.detect.outputs.language" in output_val

    def test_has_checkout_step(self, detect):
        step_uses = [s.get("uses", "") for s in detect["steps"]]
        assert any("actions/checkout" in u for u in step_uses)

    def test_detect_step_has_id(self, detect):
        step_ids = [s.get("id") for s in detect["steps"]]
        assert "detect" in step_ids

    def test_detect_step_uses_working_directory_input(self, detect):
        detect_step = next(s for s in detect["steps"] if s.get("id") == "detect")
        wd = detect_step.get("working-directory", "")
        assert "inputs.working-directory" in wd

    def test_detect_step_has_run_script(self, detect):
        detect_step = next(s for s in detect["steps"] if s.get("id") == "detect")
        assert "run" in detect_step
        script = detect_step["run"]
        assert "package.json" in script
        assert "requirements.txt" in script
        assert "pyproject.toml" in script
        assert "go.mod" in script
        assert "GITHUB_OUTPUT" in script

    def test_detect_script_covers_all_languages(self, detect):
        """
        Verify the detect job's embedded script includes detection outputs for all supported languages.
        
        Asserts that the `run` script of the step with id "detect" contains the strings 'language=node', 'language=python', 'language=go', and 'language=unknown'.
        """
        detect_step = next(s for s in detect["steps"] if s.get("id") == "detect")
        script = detect_step["run"]
        assert "language=node" in script
        assert "language=python" in script
        assert "language=go" in script
        assert "language=unknown" in script


# ---------------------------------------------------------------------------
# lint job
# ---------------------------------------------------------------------------


class TestLintJob:
    @pytest.fixture
    def lint(self, workflow):
        """
        Get the `lint` job mapping from a parsed workflow document.
        
        Parameters:
            workflow (dict): Parsed YAML workflow as a mapping (the result of yaml.safe_load).
        
        Returns:
            dict: Mapping representing the `lint` job definition under `workflow["jobs"]`.
        """
        return workflow["jobs"]["lint"]

    def test_needs_detect(self, lint):
        """
        Verify the lint job declares a dependency on the detect job.
        
        Parameters:
        	lint (dict): The parsed workflow mapping for the "lint" job (i.e., workflow["jobs"]["lint"]). The test asserts that the job's `needs` entry is either the string "detect" or a list that includes "detect".
        """
        needs = lint.get("needs")
        if isinstance(needs, list):
            assert "detect" in needs
        else:
            assert needs == "detect"

    def test_condition_uses_run_lint_input(self, lint):
        assert "run-lint" in str(lint.get("if", ""))

    def test_has_checkout_step(self, lint):
        """
        Verify the lint job includes a checkout step using the actions/checkout action.
        
        Asserts that at least one step in the provided `lint` job has a `uses` field referencing `actions/checkout`.
        """
        step_uses = [s.get("uses", "") for s in lint["steps"]]
        assert any("actions/checkout" in u for u in step_uses)

    def test_node_setup_conditional_on_language(self, lint):
        """
        Verifies the lint job includes a Node setup step guarded by a condition that depends on the detected Node language.
        
        Asserts a step using `setup-node` (identified by `uses`) exists in the provided `lint` job and that the step's `if` expression contains the substring `"node"`.
        
        Parameters:
            lint (dict): The parsed `lint` job mapping from the workflow YAML.
        """
        setup_step = next(
            (s for s in lint["steps"] if "setup-node" in s.get("uses", "")), None
        )
        assert setup_step is not None
        assert "node" in str(setup_step.get("if", ""))

    def test_node_setup_uses_node_version_input(self, lint):
        setup_step = next(
            (s for s in lint["steps"] if "setup-node" in s.get("uses", "")), None
        )
        assert setup_step is not None
        assert "inputs.node-version" in str(setup_step.get("with", {}))

    def test_node_setup_caches_npm(self, lint):
        setup_step = next(
            (s for s in lint["steps"] if "setup-node" in s.get("uses", "")), None
        )
        assert setup_step["with"].get("cache") == "npm"

    def test_lint_run_step_conditional_on_language(self, lint):
        run_step = next(
            (s for s in lint["steps"] if "run" in s and "npm" in str(s.get("run", ""))),
            None,
        )
        assert run_step is not None
        assert "node" in str(run_step.get("if", ""))

    def test_lint_run_uses_npm_ci_ignore_scripts(self, lint):
        run_step = next(
            (s for s in lint["steps"] if "npm ci" in str(s.get("run", ""))), None
        )
        assert run_step is not None
        assert "--ignore-scripts" in run_step["run"]

    def test_lint_run_uses_npm_run_lint(self, lint):
        """
        Asserts the lint job executes "npm run lint".
        
        Searches the lint job's steps for the step that runs npm (identified by containing "npm ci") and asserts that step's run command includes "npm run lint".
        
        Parameters:
            lint (dict): Parsed mapping of the `lint` job from the workflow YAML.
        """
        run_step = next(
            (s for s in lint["steps"] if "npm ci" in str(s.get("run", ""))), None
        )
        assert "npm run lint" in run_step["run"]

    def test_lint_run_uses_working_directory_input(self, lint):
        """
        Asserts the lint job's npm run step uses the workflow `inputs.working-directory`.
        
        Finds the step whose `run` contains `npm ci` and verifies that its `working-directory`
        field references `inputs.working-directory`.
        
        Parameters:
        	lint (mapping): The parsed `jobs.lint` mapping from the workflow YAML.
        """
        run_step = next(
            (s for s in lint["steps"] if "npm ci" in str(s.get("run", ""))), None
        )
        assert "inputs.working-directory" in str(run_step.get("working-directory", ""))


# ---------------------------------------------------------------------------
# test job
# ---------------------------------------------------------------------------


class TestTestJob:
    @pytest.fixture
    def test_job(self, workflow):
        """
        Retrieve the `test` job mapping from the parsed workflow document.
        
        Returns:
            dict: The dictionary representing the `test` job specification from `workflow["jobs"]`.
        """
        return workflow["jobs"]["test"]

    def test_needs_detect(self, test_job):
        needs = test_job.get("needs")
        if isinstance(needs, list):
            assert "detect" in needs
        else:
            assert needs == "detect"

    def test_condition_uses_run_tests_input(self, test_job):
        assert "run-tests" in str(test_job.get("if", ""))

    def test_has_checkout_step(self, test_job):
        step_uses = [s.get("uses", "") for s in test_job["steps"]]
        assert any("actions/checkout" in u for u in step_uses)

    def test_node_setup_conditional_on_language(self, test_job):
        setup_step = next(
            (s for s in test_job["steps"] if "setup-node" in s.get("uses", "")), None
        )
        assert setup_step is not None
        assert "node" in str(setup_step.get("if", ""))

    def test_node_setup_caches_npm(self, test_job):
        setup_step = next(
            (s for s in test_job["steps"] if "setup-node" in s.get("uses", "")), None
        )
        assert setup_step["with"].get("cache") == "npm"

    def test_test_run_uses_npm_ci_without_ignore_scripts(self, test_job):
        """
        Asserts the test job runs `npm ci` without the `--ignore-scripts` flag.
        """
        run_step = next(
            (s for s in test_job["steps"] if "npm ci" in str(s.get("run", ""))), None
        )
        assert run_step is not None
        assert "--ignore-scripts" not in run_step["run"]

    def test_test_run_uses_npm_test(self, test_job):
        run_step = next(
            (s for s in test_job["steps"] if "npm ci" in str(s.get("run", ""))), None
        )
        assert "npm test" in run_step["run"]


# ---------------------------------------------------------------------------
# security job
# ---------------------------------------------------------------------------


class TestSecurityJob:
    @pytest.fixture
    def security(self, workflow):
        """
        Retrieve the top-level "security" job mapping from the parsed workflow.
        
        Parameters:
            workflow (dict): Parsed GitHub Actions workflow structure (as returned by yaml.safe_load).
        
        Returns:
            dict: The mapping representing the `security` job under `workflow["jobs"]`.
        """
        return workflow["jobs"]["security"]

    def test_needs_detect(self, security):
        needs = security.get("needs")
        if isinstance(needs, list):
            assert "detect" in needs
        else:
            assert needs == "detect"

    def test_condition_uses_run_security_input(self, security):
        assert "run-security" in str(security.get("if", ""))

    def test_npm_audit_step_conditional_on_node(self, security):
        audit_step = next(
            (s for s in security["steps"] if "npm audit" in str(s.get("run", ""))),
            None,
        )
        assert audit_step is not None
        assert "node" in str(audit_step.get("if", ""))

    def test_npm_audit_uses_moderate_level(self, security):
        audit_step = next(
            (s for s in security["steps"] if "npm audit" in str(s.get("run", ""))),
            None,
        )
        assert "--audit-level=moderate" in audit_step["run"]

    def test_npm_audit_does_not_fail_pipeline(self, security):
        """Ensure the npm audit command appends '|| true' to prevent audit failures from failing the workflow."""
        audit_step = next(
            (s for s in security["steps"] if "npm audit" in str(s.get("run", ""))),
            None,
        )
        assert "|| true" in audit_step["run"]

    def test_snyk_step_conditional_on_token(self, security):
        snyk_step = next(
            (s for s in security["steps"] if "snyk" in s.get("uses", "").lower()),
            None,
        )
        assert snyk_step is not None
        assert "SNYK_TOKEN" in str(snyk_step.get("if", ""))

    def test_snyk_step_continue_on_error(self, security):
        snyk_step = next(
            (s for s in security["steps"] if "snyk" in s.get("uses", "").lower()),
            None,
        )
        assert snyk_step.get("continue-on-error") is True

    def test_snyk_step_passes_token_env(self, security):
        snyk_step = next(
            (s for s in security["steps"] if "snyk" in s.get("uses", "").lower()),
            None,
        )
        assert "SNYK_TOKEN" in snyk_step.get("env", {})


# ---------------------------------------------------------------------------
# ai-review job
# ---------------------------------------------------------------------------


class TestAiReviewJob:
    @pytest.fixture
    def ai_review(self, workflow):
        """
        Get the 'ai-review' job definition from the parsed workflow.
        
        Parameters:
            workflow (dict): Parsed GitHub Actions workflow mapping as returned by yaml.safe_load.
        
        Returns:
            dict: The mapping representing the 'ai-review' job configuration.
        """
        return workflow["jobs"]["ai-review"]

    def test_no_needs_detect(self, ai_review):
        """ai-review does not depend on detect."""
        assert "needs" not in ai_review

    def test_condition_requires_run_ai_review_and_pull_request(self, ai_review):
        condition = str(ai_review.get("if", ""))
        assert "run-ai-review" in condition
        assert "pull_request" in condition

    def test_permissions_contents_read(self, ai_review):
        """
        Assert that the `ai-review` job's permissions grant read access to repository contents.
        
        Parameters:
            ai_review (dict): The parsed `ai-review` job mapping from the workflow YAML.
        """
        perms = ai_review.get("permissions", {})
        assert perms.get("contents") == "read"

    def test_permissions_pull_requests_write(self, ai_review):
        """
        Assert the ai-review job grants write permission for pull requests.
        
        Checks that the job's `permissions` mapping contains `"pull-requests": "write"`.
        """
        perms = ai_review.get("permissions", {})
        assert perms.get("pull-requests") == "write"

    def test_has_checkout_step(self, ai_review):
        step_uses = [s.get("uses", "") for s in ai_review["steps"]]
        assert any("actions/checkout" in u for u in step_uses)

    def test_claude_review_step_conditional_on_api_key(self, ai_review):
        claude_step = next(
            (
                s
                for s in ai_review["steps"]
                if "claude-code-action" in s.get("uses", "")
            ),
            None,
        )
        assert claude_step is not None
        assert "ANTHROPIC_API_KEY" in str(claude_step.get("if", ""))

    def test_claude_review_step_specifies_model(self, ai_review):
        """
        Asserts the Claude code-action step specifies a sonnet model.
        
        Verifies that the ai-review job contains a step using `claude-code-action` and that the step's `with.model` includes the substring `claude-sonnet`.
        
        Parameters:
            ai_review (dict): The parsed `ai-review` job mapping from the workflow YAML, expected to include a `steps` sequence where each step is a mapping that may contain `uses` and `with` keys.
        """
        claude_step = next(
            (
                s
                for s in ai_review["steps"]
                if "claude-code-action" in s.get("uses", "")
            ),
            None,
        )
        assert "model" in claude_step.get("with", {})
        # Should reference a specific sonnet model
        assert "claude-sonnet" in claude_step["with"]["model"]

    def test_claude_review_step_specifies_timeout(self, ai_review):
        claude_step = next(
            (
                s
                for s in ai_review["steps"]
                if "claude-code-action" in s.get("uses", "")
            ),
            None,
        )
        assert claude_step["with"].get("timeout_minutes") == 10

    def test_claude_review_passes_api_key(self, ai_review):
        """
        Verifies the AI review step for the Claude action includes an `anthropic_api_key` input that references the `ANTHROPIC_API_KEY` secret.
        
        Checks that a step using `claude-code-action` provides a `with.anthropic_api_key` key and that its value contains a reference to `ANTHROPIC_API_KEY`.
        """
        claude_step = next(
            (
                s
                for s in ai_review["steps"]
                if "claude-code-action" in s.get("uses", "")
            ),
            None,
        )
        assert "anthropic_api_key" in claude_step.get("with", {})
        assert "ANTHROPIC_API_KEY" in str(claude_step["with"]["anthropic_api_key"])


# ---------------------------------------------------------------------------
# Language detection shell script logic
# ---------------------------------------------------------------------------
#
# These tests extract the exact shell logic from the workflow and run it
# against temporary directories simulating different project layouts.
# ---------------------------------------------------------------------------

DETECT_SCRIPT = """
if [ -f "package.json" ]; then
  echo "language=node" >> $GITHUB_OUTPUT
elif [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
  echo "language=python" >> $GITHUB_OUTPUT
elif [ -f "go.mod" ]; then
  echo "language=go" >> $GITHUB_OUTPUT
else
  echo "language=unknown" >> $GITHUB_OUTPUT
fi
"""


def _run_detect_script(tmpdir, files_to_create):
    """
    Run the embedded language-detection script in a temporary directory and return the detected language.
    
    Parameters:
        tmpdir (str | pathlib.Path): Path to the directory where files will be created and the script executed.
        files_to_create (Iterable[str]): Filenames to create inside `tmpdir` before running the detection script.
    
    Returns:
        str: The language value parsed from the `language=...` line written to the `GITHUB_OUTPUT` file.
    
    Raises:
        AssertionError: If the detection script exits with a non-zero status or if the output file does not contain a line starting with `language=`.
    """
    for fname in files_to_create:
        open(os.path.join(tmpdir, fname), "w").close()
    output_file = os.path.join(tmpdir, "github_output")
    env = {**os.environ, "GITHUB_OUTPUT": output_file}
    result = subprocess.run(
        ["bash", "-c", DETECT_SCRIPT],
        cwd=tmpdir,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    with open(output_file) as f:
        line = f.read().strip()
    assert line.startswith("language="), f"Unexpected output: {line}"
    return line.split("=", 1)[1]


class TestDetectScript:
    def test_package_json_detects_node(self, tmp_path):
        lang = _run_detect_script(str(tmp_path), ["package.json"])
        assert lang == "node"

    def test_requirements_txt_detects_python(self, tmp_path):
        lang = _run_detect_script(str(tmp_path), ["requirements.txt"])
        assert lang == "python"

    def test_pyproject_toml_detects_python(self, tmp_path):
        lang = _run_detect_script(str(tmp_path), ["pyproject.toml"])
        assert lang == "python"

    def test_go_mod_detects_go(self, tmp_path):
        lang = _run_detect_script(str(tmp_path), ["go.mod"])
        assert lang == "go"

    def test_empty_directory_detects_unknown(self, tmp_path):
        lang = _run_detect_script(str(tmp_path), [])
        assert lang == "unknown"

    def test_package_json_takes_priority_over_requirements_txt(self, tmp_path):
        """Node is checked first; a mixed repo with package.json → node."""
        lang = _run_detect_script(str(tmp_path), ["package.json", "requirements.txt"])
        assert lang == "node"

    def test_package_json_takes_priority_over_pyproject_toml(self, tmp_path):
        lang = _run_detect_script(str(tmp_path), ["package.json", "pyproject.toml"])
        assert lang == "node"

    def test_package_json_takes_priority_over_go_mod(self, tmp_path):
        lang = _run_detect_script(str(tmp_path), ["package.json", "go.mod"])
        assert lang == "node"

    def test_requirements_txt_takes_priority_over_go_mod(self, tmp_path):
        """Python is checked before Go."""
        lang = _run_detect_script(str(tmp_path), ["requirements.txt", "go.mod"])
        assert lang == "python"

    def test_pyproject_toml_takes_priority_over_go_mod(self, tmp_path):
        lang = _run_detect_script(str(tmp_path), ["pyproject.toml", "go.mod"])
        assert lang == "python"

    def test_both_python_files_present_detects_python(self, tmp_path):
        lang = _run_detect_script(
            str(tmp_path), ["requirements.txt", "pyproject.toml"]
        )
        assert lang == "python"

    def test_unrelated_files_detect_unknown(self, tmp_path):
        """Presence of unrecognised files like Makefile should yield unknown."""
        lang = _run_detect_script(str(tmp_path), ["Makefile", "README.md"])
        assert lang == "unknown"

    def test_go_mod_is_case_sensitive(self, tmp_path):
        """go.mod detection is case-sensitive; Go.mod should not match."""
        lang = _run_detect_script(str(tmp_path), ["Go.mod"])
        assert lang == "unknown"

    def test_package_json_is_case_sensitive(self, tmp_path):
        """Package.json (capital P) should not be detected as node."""
        lang = _run_detect_script(str(tmp_path), ["Package.json"])
        assert lang == "unknown"

    def test_script_writes_exactly_one_language(self, tmp_path):
        """The GITHUB_OUTPUT file should have exactly one language= line."""
        files = ["package.json"]
        for fname in files:
            open(os.path.join(str(tmp_path), fname), "w").close()
        output_file = os.path.join(str(tmp_path), "github_output")
        env = {**os.environ, "GITHUB_OUTPUT": output_file}
        subprocess.run(["bash", "-c", DETECT_SCRIPT], cwd=str(tmp_path), env=env)
        with open(output_file) as f:
            lines = [l for l in f.read().splitlines() if l.startswith("language=")]
        assert len(lines) == 1


# ---------------------------------------------------------------------------
# Regression: correct YAML nesting (the core fix of this PR)
# ---------------------------------------------------------------------------


class TestIndentationRegression:
    """Verify the indentation fix did not accidentally alter logical structure."""

    def test_workflow_call_has_exactly_two_keys(self, workflow):
        """workflow_call should have only 'inputs' and 'secrets'."""
        wc = workflow[True]["workflow_call"]
        assert set(wc.keys()) == {"inputs", "secrets"}

    def test_inputs_count_is_seven(self, workflow):
        inputs = workflow[True]["workflow_call"]["inputs"]
        assert len(inputs) == 7

    def test_secrets_count_is_two(self, workflow):
        secrets = workflow[True]["workflow_call"]["secrets"]
        assert len(secrets) == 2

    def test_jobs_count_is_five(self, workflow):
        assert len(workflow["jobs"]) == 5

    def test_detect_job_has_two_steps(self, workflow):
        assert len(workflow["jobs"]["detect"]["steps"]) == 2

    def test_lint_job_has_three_steps(self, workflow):
        # checkout + setup-node + lint run
        assert len(workflow["jobs"]["lint"]["steps"]) == 3

    def test_test_job_has_three_steps(self, workflow):
        # checkout + setup-node + test run
        assert len(workflow["jobs"]["test"]["steps"]) == 3

    def test_security_job_has_three_steps(self, workflow):
        assert len(workflow["jobs"]["security"]["steps"]) == 3

    def test_ai_review_job_has_two_steps(self, workflow):
        assert len(workflow["jobs"]["ai-review"]["steps"]) == 2
