// Legacy shared overlay fixture for the unmigrated Claude and pstack probes only.
// Adoption acceptance now uses content-probes.py and the released candidate CLI.
// The local Source supplies built bytes; it is not an attestation test.
package cli

import (
	"crypto/sha256"
	"encoding/hex"
	"os"
	"path/filepath"
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
