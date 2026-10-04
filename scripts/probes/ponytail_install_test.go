// Overlay into the pinned engine's internal/cli package alongside catalog_adoption_test.go.
// PROBE_SNAPSHOT and PROBE_SOURCE_COMMIT select a locally built candidate, not a publication.
package cli

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestPonytailProjectInstall(t *testing.T) {
	if os.Getenv("PROBE_SNAPSHOT") == "" || os.Getenv("PROBE_SOURCE_COMMIT") == "" {
		t.Fatal("PROBE_SNAPSHOT and PROBE_SOURCE_COMMIT are required")
	}
	for _, surface := range []string{"codex", "claude", "opencode"} {
		for _, selection := range []string{"complete", "skill", "instruction"} {
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
				} else if surface == "opencode" {
					skillRoot = ".opencode/skills"
				}
				instructionPath := filepath.Join(project, instruction)
				if err := os.WriteFile(instructionPath, []byte("# Existing project guidance\n\nKeep local conventions.\n"), 0644); err != nil {
					t.Fatal(err)
				}
				if selection == "skill" {
					run("install", "argote", "--surface", surface, "--resource", "instruction:guidance", "--json")
				}
				originalInstructions := read(instructionPath)
				args := []string{"install", "ponytail", "--surface", surface, "--json"}
				if selection == "skill" {
					args = append(args, "--resource", "skill:ponytail")
				} else if selection == "instruction" {
					args = append(args, "--resource", "instruction:ponytail-guidance")
				}
				beforeProject, beforeHome := snapshotTree(t, project), snapshotTree(t, home)
				run(append(append([]string{}, args...), "--dry-run")...)
				if snapshotTree(t, project) != beforeProject || snapshotTree(t, home) != beforeHome {
					t.Fatal("preview mutated project or home")
				}
				run(args...)
				run("verify", "--json")
				instructions := read(instructionPath)
				if !strings.Contains(instructions, strings.TrimSpace(originalInstructions)) {
					t.Fatal("Ponytail replaced existing or Argote instructions")
				}
				if hasGuidance := strings.Contains(instructions, "# Ponytail, lazy senior dev mode"); hasGuidance != (selection != "skill") {
					t.Fatal("persistent guidance does not match resource selection")
				}
				for _, name := range []string{"ponytail", "ponytail-review", "ponytail-audit", "ponytail-debt", "ponytail-gain", "ponytail-help"} {
					path := filepath.Join(project, skillRoot, name, "SKILL.md")
					want := selection == "complete" || (selection == "skill" && name == "ponytail")
					if want {
						if !strings.Contains(read(path), "name: "+name+"\n") {
							t.Fatalf("wrong skill projected at %s", path)
						}
					} else if _, err := os.Stat(path); !os.IsNotExist(err) {
						t.Fatalf("unselected skill %s was installed: %v", name, err)
					}
				}
				if !strings.Contains(read(filepath.Join(project, "PACKY-NOTICES.md")), "Copyright (c) 2026 DietrichGebert") {
					t.Fatal("missing upstream attribution")
				}
				if selection != "skill" {
					before := snapshotTree(t, project)
					out, err := executeCommand(t, NewRootCommand(opts), "install", "argote", "--surface", surface, "--resource", "instruction:guidance", "--dry-run", "--json")
					if err == nil || !strings.Contains(out, "projection_collision") || snapshotTree(t, project) != before {
						t.Fatalf("expected unchanged project on shared instruction path collision: %v\n%s", err, out)
					}
				}
				for _, path := range []string{".codex/config.toml", ".claude/settings.json", "xdg/opencode/opencode.json"} {
					if _, err := os.Stat(filepath.Join(home, path)); !os.IsNotExist(err) {
						t.Fatalf("project installation changed personal host configuration %s: %v", path, err)
					}
				}
				run("uninstall", "ponytail", "--surface", surface)
				if selection == "skill" {
					run("verify", "--json")
				} else {
					for _, name := range []string{"packy.json", "packy.lock.json", "PACKY-NOTICES.md"} {
						if _, err := os.Stat(filepath.Join(project, name)); !os.IsNotExist(err) {
							t.Fatalf("last Pack removal retained %s: %v", name, err)
						}
					}
				}
				if strings.TrimSpace(read(instructionPath)) != strings.TrimSpace(originalInstructions) {
					t.Fatal("uninstall changed existing or Argote guidance")
				}
				paths, err := filepath.Glob(filepath.Join(project, skillRoot, "ponytail*"))
				if err != nil || len(paths) != 0 {
					t.Fatalf("uninstall left Ponytail skills: %v %v", paths, err)
				}
			})
		}
	}
}
