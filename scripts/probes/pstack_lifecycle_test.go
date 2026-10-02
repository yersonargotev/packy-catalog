// Copy with catalog_adoption_test.go into the pinned engine's internal/cli package.
package cli

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestPstackCatalogVariants(t *testing.T) {
	for _, scope := range []string{"global", "project"} {
		t.Run(scope, func(t *testing.T) {
			home, project := t.TempDir(), t.TempDir()
			writeTestGitWorktree(t, project)
			source := &catalogSourceFixture{release: adoptionRelease(t, os.Getenv("PROBE_OLD_SNAPSHOT"), os.Getenv("PROBE_OLD_COMMIT"))}
			opts := Options{Env: MapEnv{"HOME": home, "XDG_CONFIG_HOME": filepath.Join(home, "xdg"), "PATH": ""}, Runner: &fakeRunner{}, Terminal: &fakeTerminal{interactive: true, approve: true}, Getwd: func() (string, error) { return project, nil }, CatalogSource: source}
			run := func(args ...string) string {
				t.Helper()
				out, err := executeCommand(t, NewRootCommand(opts), args...)
				if err != nil {
					t.Fatalf("%v: %v\n%s", args, err, out)
				}
				return out
			}
			apply, remove, base := "activate", "deactivate", home
			if scope == "project" {
				apply, remove, base = "install", "uninstall", project
			}
			target := func(surface string) string {
				directory := map[string]string{"codex": ".agents/skills", "claude": ".claude/skills", "opencode": "xdg/opencode/skills"}[surface]
				if scope == "project" && surface == "opencode" {
					directory = ".opencode/skills"
				}
				return filepath.Join(base, directory)
			}
			check := func(surface, label string) {
				t.Helper()
				data, err := os.ReadFile(filepath.Join(target(surface), "reflect/SKILL.md"))
				if err != nil || !strings.Contains(string(data), "## "+label+" execution") {
					t.Fatalf("wrong %s definition: %v", surface, err)
				}
			}
			run("init")
			run(apply, "pstack", "--surface", "codex")
			run(apply, "pstack", "--surface", "claude")
			untouched := snapshotTree(t, target("claude"))
			source.release = adoptionRelease(t, os.Getenv("PROBE_SNAPSHOT"), os.Getenv("PROBE_SOURCE_COMMIT"))
			run("catalog", "refresh")
			update := func(surface string) {
				args := []string{"update", "pstack", "--surface", surface}
				if scope == "project" {
					args = append(args, "--project")
				}
				run(args...)
			}
			update("codex")
			check("codex", "Codex")
			if untouched != snapshotTree(t, target("claude")) {
				t.Fatal("Codex update changed Claude tree")
			}
			codex := snapshotTree(t, target("codex"))
			update("claude")
			check("claude", "Claude Code")
			if codex != snapshotTree(t, target("codex")) {
				t.Fatal("Claude update changed Codex tree")
			}
			claude := snapshotTree(t, target("claude"))
			beforeHome, beforeProject := snapshotTree(t, home), snapshotTree(t, project)
			out, err := executeCommand(t, NewRootCommand(opts), apply, "pstack", "--surface", "opencode")
			if err == nil || !strings.Contains(out+err.Error(), "deterministic coexistence is not verified") {
				t.Fatalf("expected OpenCode coexistence block: %v\n%s", err, out)
			}
			if beforeHome != snapshotTree(t, home) || beforeProject != snapshotTree(t, project) {
				t.Fatal("blocked coexistence mutated state")
			}
			helper := filepath.Join(target("codex"), "poteto-mode/scripts/bootstrap.ts")
			original, err := os.ReadFile(helper)
			if err != nil {
				t.Fatal(err)
			}
			if err = os.WriteFile(helper, append(original, []byte("\n// drift probe\n")...), 0644); err != nil {
				t.Fatal(err)
			}
			if out, err := executeCommand(t, NewRootCommand(opts), remove, "pstack", "--surface", "codex"); err == nil {
				t.Fatalf("helper drift allowed removal: %s", out)
			}
			if err = os.WriteFile(helper, original, 0644); err != nil {
				t.Fatal(err)
			}
			run(remove, "pstack", "--surface", "codex")
			if claude != snapshotTree(t, target("claude")) {
				t.Fatal("Codex removal changed Claude tree")
			}
			run(remove, "pstack", "--surface", "claude")
			run(apply, "pstack", "--surface", "opencode")
			check("opencode", "OpenCode")
			run(remove, "pstack", "--surface", "opencode")
			// Selected dependencies must include variant-only requirements.
			run(apply, "pstack", "--surface", "codex", "--resource", "skill:architect")
			for _, id := range []string{"principle-exhaust-the-design-space", "principle-fix-root-causes", "principle-prove-it-works", "principle-redesign-from-first-principles"} {
				if _, err := os.Stat(filepath.Join(target("codex"), id, "SKILL.md")); err != nil {
					t.Fatalf("missing effective dependency %s: %v", id, err)
				}
			}
			run(remove, "pstack", "--surface", "codex")
			t.Log("targeted updates/removals preserve other host; drift and unverified OpenCode coexistence block; effective dependencies install")
		})
	}
}
