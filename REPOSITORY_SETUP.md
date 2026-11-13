# Publish the Permission Delta starter project

The source bundle is ready for a private GitHub repository named `permission-delta` under `AGENTPROOFINC`.

## GitHub Desktop on Mac

1. Install GitHub Desktop from https://desktop.github.com/ and sign in to `AGENTPROOFINC`.
2. Extract this bundle. In GitHub Desktop choose **File → Add Local Repository**, then select the `permission-delta` folder.
3. If GitHub Desktop says the folder is not a repository, choose **Create a Repository**, keep `main` as the branch, and use the selected project folder.
4. Review the files and confirm no real credentials or private configurations are present.
5. Choose **Publish repository**, name it `permission-delta`, and keep **Private** selected.

## Git command line

From the project folder, initialize and commit the files:

```bash
git init -b main
git add .
git commit -m "Initialize Permission Delta prototype"
```

Create an empty private repository at `https://github.com/AGENTPROOFINC/permission-delta` first, then connect and push:

```bash
git remote add origin https://github.com/AGENTPROOFINC/permission-delta.git
git push -u origin main
```

Authenticate only through GitHub's normal browser or credential-manager flow. Never paste a personal access token into chat or commit one to the repository.

## Before enabling the sample workflow

Review `.github/workflows/permission-delta.yml` and the read-only `contents: read` permission. The workflow is advisory: it writes a sanitized summary but does not approve, reject, or merge pull requests. Replace the mutable action version tags with reviewed full commit SHAs before relying on it in a high-assurance environment.

## Project naming

`Permission Delta` is a working codename, not a trademark-cleared public brand. Keep the repository private until the name, code, license, and workflow have been reviewed.
