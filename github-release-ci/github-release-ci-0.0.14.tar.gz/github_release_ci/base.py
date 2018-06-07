#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Base Code."""

from os import environ, path, getcwd
import requests as http


class Release(object):
    """Github release object."""

    def __init__(self, repo_slug, release_slug):
        """Init."""
        self.repo_slug = repo_slug
        self.release_slug = release_slug

    @property
    def release_url(self):
        """Release URL."""
        return (
            'https://api.github.com/repos/{repo_slug}/releases/{release_slug}'
        ).format(repo_slug=self.repo_slug, release_slug=self.release_slug)

    @property
    def release_query_url(self):
        """Release query URL."""
        return (
            'https://api.github.com/repos/{repo_slug}/releases'
        ).format(repo_slug=self.repo_slug)

    def get_info(self, disable_cache=False):
        """Get release info."""
        if getattr(self, "__info", None) and not disable_cache:
            return self.__info

        resp = http.get(
            self.release_url,
            auth=(environ["GITHUB_TOKEN"], ''),
            headers={"Content-Type": "application/json"}
        )
        resp.raise_for_status()
        self.__info = resp.json()
        return self.__info

    def create_release(self, tag):
        """Create a release."""
        resp = http.post(
            self.release_query_url,
            auth=(environ["GITHUB_TOKEN"], ''),
            headers={"Content-Type": "application/json"},
            json={'tag_name': tag}
        )
        resp.raise_for_status()
        self.__info = resp.json()
        return self.__info

    @property
    def asset_info(self):
        """Get asset info."""
        return self.get_info()["assets"]

    def upload_asset(self, file_path, destination_file_name=None):
        """Upload assets."""
        upload_url = None
        try:
            upload_url = self.get_info()["upload_url"]
        except http.HTTPError:
            tag = self.release_slug.split("tags/")[1]
            upload_url = self.create_release(tag)["upload_url"]
        upload_url = upload_url.replace("{?name,label}", "")
        resp = http.post(
            upload_url,
            params={"name": destination_file_name or path.basename(file_path)},
            files={"file": open(file_path, 'rb')},
            auth=(environ["GITHUB_TOKEN"], ''),
        )
        resp = resp.raise_for_status()

    def download_assets(self, out_dir=getcwd()):
        """Download the assets from the release."""
        for asset in self.asset_info:
            resp = http.get(
                self.asset_info["url"],
                auth=(environ["GITHUB_TOKEN"], ''),
                headers={"Content-Type": "application/octed-stream"}
            )
            resp.raise_for_status()
            out_path = path.join(
                out_dir, ("{}-{}").format(asset["id"], asset["name"])
            )
            with open(out_path, 'wb') as w:
                for chunk in resp.iter_content(chunk_size=128):
                    w.write(chunk)
