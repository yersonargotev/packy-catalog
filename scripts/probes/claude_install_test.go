// Overlay into the pinned engine's internal/cli package alongside catalog_adoption_test.go.
package cli

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestClaudeProjectInstall(t *testing.T) {
	if os.Getenv("PROBE_SNAPSHOT") == "" || os.Getenv("PROBE_SOURCE_COMMIT") == "" {
		t.Fatal("PROBE_SNAPSHOT and PROBE_SOURCE_COMMIT are required")
	}
	for _, surface := range []string{"codex", "claude", "opencode"} {
		for _, selection := range []string{"complete", "eli5", "html-plan"} {
			t.Run(surface+"/"+selection, func(t *testing.T) {
				home, project := t.TempDir(), t.TempDir()
				writeTestGitWorktree(t, project)
				source := &catalogSourceFixture{release: adoptionRelease(t, os.Getenv("PROBE_SNAPSHOT"), os.Getenv("PROBE_SOURCE_COMMIT"))}
				opts := Options{
					Env:    MapEnv{"HOME": home, "XDG_CONFIG_HOME": filepath.Join(home, "xdg"), "PATH": ""},
					Runner: &fakeRunner{}, Terminal: &fakeTerminal{interactive: true, approve: true},
					Getwd: func() (string, error) { return project, nil }, CatalogSource: source,
				}
				run := func(args ...string) {
					t.Helper()
					if out, err := executeCommand(t, NewRootCommand(opts), args...); err != nil {
						t.Fatalf("%v: %v\n%s", args, err, out)
					}
				}
				read := func(path string) string {
					t.Helper()
					data, err := os.ReadFile(path)
					if err != nil {
						t.Fatal(err)
					}
					return string(data)
				}
				run("init")
				instruction, skillRoot := "AGENTS.md", ".agents/skills"
				if surface == "claude" {
					instruction, skillRoot = "CLAUDE.md", ".claude/skills"
				}
				if surface == "opencode" {
					skillRoot = ".opencode/skills"
				}
				instructionPath := filepath.Join(project, instruction)
				if err := os.WriteFile(instructionPath, []byte("# Local guidance\n\nPreserve project conventions.\n"), 0644); err != nil {
					t.Fatal(err)
				}
				run("install", "argote", "--surface", surface, "--resource", "instruction:guidance", "--json")
				originalInstructions := read(instructionPath)
				args := []string{"install", "claude", "--surface", surface, "--json"}
				if selection != "complete" {
					args = append(args, "--resource", "skill:"+selection)
				}
				beforeProject, beforeHome := snapshotTree(t, project), snapshotTree(t, home)
				run(append(append([]string{}, args...), "--dry-run")...)
				if snapshotTree(t, project) != beforeProject || snapshotTree(t, home) != beforeHome {
					t.Fatal("preview mutated project or home")
				}
				run(args...)
				run("verify", "--json")
				for _, name := range []string{"eli5", "html-plan"} {
					path := filepath.Join(project, skillRoot, name, "SKILL.md")
					want := selection == "complete" || selection == name
					if want {
						if !strings.Contains(read(path), "name: "+name+"\n") {
							t.Fatalf("wrong skill at %s", path)
						}
					} else if _, err := os.Stat(path); !os.IsNotExist(err) {
						t.Fatalf("unselected skill installed: %s", path)
					}
				}
				if selection != "eli5" {
					for _, name := range []string{"runtime/htmlplan.js", "runtime/htmlplan.css", "runtime/pack.mjs", "references/blocks.md", "examples/scheduled-send.html"} {
						if _, err := os.Stat(filepath.Join(project, skillRoot, "html-plan", name)); err != nil {
							t.Fatalf("missing runtime closure %s: %v", name, err)
						}
					}
				}
				notices := read(filepath.Join(project, "PACKY-NOTICES.md"))
				if !strings.Contains(notices, "Apache License") {
					t.Fatal("repository license missing")
				}
				for _, name := range []string{"eli5", "html-plan"} {
					included := strings.Contains(notices, `"name": "`+name+`"`)
					if included != (selection == "complete" || selection == name) {
						t.Fatalf("wrong notice closure for %s", name)
					}
				}
				if read(instructionPath) != originalInstructions {
					t.Fatal("installation changed project guidance")
				}
				if snapshotTree(t, home) != beforeHome {
					t.Fatal("installation changed personal configuration")
				}
				run("uninstall", "claude", "--surface", surface)
				run("verify", "--json")
				if read(instructionPath) != originalInstructions {
					t.Fatal("uninstall changed Argote or local guidance")
				}
				for _, name := range []string{"eli5", "html-plan"} {
					if _, err := os.Stat(filepath.Join(project, skillRoot, name)); !os.IsNotExist(err) {
						t.Fatalf("uninstall retained %s", name)
					}
				}
			})
		}
	}
}
