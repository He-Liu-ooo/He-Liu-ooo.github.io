# Liu He Academic Homepage

This repository is the source for Liu He's static English academic homepage, intended to be published with GitHub Pages at https://he-liu-ooo.github.io. The site uses plain HTML and CSS with no build step.

## Preview Locally

From the repository root, start a local server:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

The server runs in the foreground; use another terminal to run the checks and a browser to open http://localhost:8000. Binding to loopback avoids exposing the repository, including any ignored root `CV.pdf`, on the lab network.

Run the checks with:

```sh
python3 -m unittest discover -s tests -v
```

## Update Public Content

### Profile photo

Replace `files/profile/profile-placeholder.svg` with an approved image under `files/profile/`. Update the image `src` in `index.html` while preserving descriptive alternative text and explicit dimensions.

### Research interests

Replace the exact placeholder `Research interests statement forthcoming.` only with text approved by the owner.

### Papers and slides

Place redistributable papers under `files/papers/` and slides under `files/slides/`, then add only verified links to `index.html`. Use DOI or publisher links when redistribution is not permitted.

### Public CV

Never publish the private root `CV.pdf`. Create a sanitized public copy without a phone number, full address, or other unapproved sensitive information, place it under `files/cv/`, and only then enable the CV link in `index.html`.

## Publish with GitHub Pages

1. Create the public GitHub repository `He-Liu-ooo.github.io`.
2. Add it as the Git remote named `origin` and push the `main` branch.
3. In repository **Settings → Pages**, configure deployment from the `main` branch at the repository root.
4. Verify the published site at https://he-liu-ooo.github.io.

To add a custom domain securely:

1. First, verify the custom domain in your GitHub account settings.
2. Then, add the verified domain in repository **Settings → Pages**.
3. Finally, configure the required DNS records with your domain registrar.

Do not use wildcard DNS records. Follow [GitHub's official managing-a-custom-domain documentation](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site) for verification, supported DNS records, and HTTPS setup.
