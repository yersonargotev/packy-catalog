// Copy into the pinned engine's internal/cli directory; run TestCatalogAdoption.
// The local Source supplies downloaded/built bytes. It is not an attestation test.
package cli

import (
	"crypto/sha256"
	"encoding/hex"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/yersonargotev/packy/internal/catalogstore"
)

func adoptionRelease(t *testing.T, directory, commit string) catalogstore.Release {
	t.Helper()
	r := catalogstore.Release{Repository: "yersonargotev/packy-catalog", Tag: "catalog-" + commit, Commit: commit, Publisher: "github-actions[bot]", Published: true, Immutable: true, AttestationVerified: true}
	for _, name := range []string{"catalog-snapshot.tar.gz", "SHA256SUMS"} {
		data, err := os.ReadFile(filepath.Join(directory, name))
		if err != nil {
			t.Fatal(err)
		}
		digest := sha256.Sum256(data)
		r.Assets = append(r.Assets, catalogstore.Asset{Name: name, Data: data, SHA256: hex.EncodeToString(digest[:])})
	}
	return r
}

func TestCatalogAdoption(t *testing.T) {
	home, project := t.TempDir(), t.TempDir()
	writeTestGitWorktree(t, project)
	commit := os.Getenv("PROBE_SOURCE_COMMIT")
	source := &catalogSourceFixture{release: adoptionRelease(t, os.Getenv("PROBE_SNAPSHOT"), commit)}
	opts := Options{Env: MapEnv{"HOME": home, "XDG_CONFIG_HOME": filepath.Join(home, "xdg"), "PATH": ""}, Runner: &fakeRunner{}, Terminal: &fakeTerminal{interactive: true, approve: true}, Getwd: func() (string, error) { return project, nil }, CatalogSource: source}
	if out, err := executeCommand(t, NewRootCommand(opts), "init"); err != nil {
		t.Fatalf("init: %v\n%s", err, out)
	}
	selection := filepath.Join(catalogstore.DefaultDataRoot(home), "catalog", "selected.json")
	before, err := os.ReadFile(selection)
	if err != nil {
		t.Fatal(err)
	}
	if rejected := os.Getenv("PROBE_REJECT_SNAPSHOT"); rejected != "" {
		source.release = adoptionRelease(t, rejected, os.Getenv("PROBE_REJECT_COMMIT"))
		out, err := executeCommand(t, NewRootCommand(opts), "catalog", "refresh")
		if err == nil || !strings.Contains(err.Error()+out, "newer Packy engine") {
			t.Fatalf("expected incompatible rejection: %v\n%s", err, out)
		}
		after, err := os.ReadFile(selection)
		if err != nil || string(before) != string(after) {
			t.Fatal("failed acquisition changed selection")
		}
		if out, err := executeCommand(t, NewRootCommand(opts), "list"); err != nil {
			t.Fatalf("old catalog unusable after rejection: %v\n%s", err, out)
		}
		t.Log("incompatible snapshot rejected; previous selection and catalog remain usable")
		return
	}
	for _, surface := range []string{"codex", "claude", "opencode"} {
		for _, command := range []string{"install", "uninstall"} {
			if out, err := executeCommand(t, NewRootCommand(opts), command, "emil", "--surface", surface); err != nil {
				t.Fatalf("%s %s: %v\n%s", command, surface, err, out)
			}
		}
	}
	t.Log("complete snapshot acquired; common Emil resources installed and uninstalled on all three surfaces")
}
