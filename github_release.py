import requests
import zipfile
import io
import hashlib
import copy
import os


def download_all_release(owner, repo, output, f_get_file_name, platform):
    if not os.path.exists(output):
        os.makedirs(output)

    tag_to_sha = {}
    for page in range(1, 11):
        page_tag = {item['name']: item['commit']['sha'] for item in requests.get(f"https://api.github.com/repos/{owner}/{repo}/tags?per_page=100&page={page}").json()}
        if not page_tag:
            break
        tag_to_sha.update(page_tag)
    
    releases = []
    for page in range(1, 11):
        page_release = requests.get(f"https://api.github.com/repos/{owner}/{repo}/releases?per_page=100&page={page}").json()
        if not page_release:
            break
        releases.extend(page_release)
    print(f"Total {len(releases)} releases")

    for release in releases:
        if release['prerelease']:
            continue
        release_name = release['name']
        commit_sha = tag_to_sha[release['tag_name']]
        file_name = f_get_file_name(release_name, commit_sha)
        if os.path.exists(f"{output}/{file_name}"):
            print(f"{release_name} exist in {file_name}")
            continue
        md5 = ""
        solc = ""
        zip = False
        for asset in release['assets']:
            if "md5" in asset['name']:
                md5_download_url = asset['browser_download_url']
                md5 = requests.get(md5_download_url, timeout=600).content.decode('utf-8')
            if platform in asset['name']:
                solc_download_url = asset['browser_download_url']
                solc = copy.deepcopy(requests.get(solc_download_url, timeout=600).content)
                if "zip" in asset['name']:
                    zip = True
        if not solc:
            print(f"ERROR: {release_name} download release solc failed, assets:{[asset['name'] for asset in release['assets']]}")
            continue

        if md5:
            real_md5 = hashlib.md5(solc).hexdigest()
            if real_md5 not in md5:
                print(f"WARNING: {release_name} md5 check failed\nexpect:\n{md5}\nactual={real_md5}")

        if zip:
            with zipfile.ZipFile(io.BytesIO(solc)) as z:
                solc_name = next((name for name in z.namelist() if 'solc' in name), None)
                if solc_name:
                    solc = z.read(solc_name)
                else:
                    print(f"ERROR: {release_name}: there is not solc file in zip, filelist={z.namelist()}")
                    continue

        path = f"{output}/{file_name}"
        with open(path, 'wb') as f:
            f.write(solc)
        os.chmod(path, 0o755)
        print(f"{release_name} saved to {path}")


if __name__ == "__main__":

    def get_file_name_tron(release_name, commit_sha):
        return f"tron_v{release_name.split('_')[0]}+commit.{commit_sha[:8]}"

    def get_file_name_ethereum(release_name, commit_sha):
        return f"v{release_name.split(' ')[1]}+commit.{commit_sha[:8]}"


    # download_all_release(
    #     output = "output/tron_solidity",
    #     owner = "tronprotocol",
    #     repo = "solidity",
    #     f_get_file_name=get_file_name_tron,
    #     platform="linux",
    # )
    
    # download_all_release(
    #     output = "output/ethereum_solidity",
    #     owner = "ethereum",
    #     repo = "solidity",
    #     f_get_file_name=get_file_name_ethereum,
    #     platform="linux",
    # )

    # download_all_release(
    #     output = "output/macos_tron_solidity",
    #     owner = "tronprotocol",
    #     repo = "solidity",
    #     f_get_file_name=get_file_name_tron,
    #     platform="mac",
    # )

    download_all_release(
        output = "output/macos_ethereum_solidity",
        owner = "ethereum",
        repo = "solidity",
        f_get_file_name=get_file_name_ethereum,
        platform="mac",
    )