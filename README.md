[![Molecule](https://github.com/iamenr0s/ansible-role-pam-hardening/actions/workflows/molecule.yml/badge.svg)](https://github.com/iamenr0s/ansible-role-pam-hardening/actions/workflows/molecule.yml) ![Ansible Role](https://img.shields.io/ansible/role/d/iamenr0s/ansible_role_pam_hardening) [![CodeFactor](https://www.codefactor.io/repository/github/iamenr0s/ansible-role-pam-hardening/badge)](https://www.codefactor.io/repository/github/iamenr0s/ansible-role-pam-hardening)

# Ansible Role: Pam Hardening

> Standalone copy of `pam_hardening` from the [iamenr0s.linux_hardening](https://github.com/iamenr0s/linux-hardening-collection) collection. Variables keep the collection-wide `linux_hardening_*` prefix.

Sole owner of PAM stack changes in this collection. Today it does one thing: **account lockout with `pam_faillock`** (lock an account for `unlock_time` seconds after `deny` failed logins). Password quality and `login.defs` belong to a later `password_policy` role.

## What it does
| Part | EL / Fedora | Debian / Ubuntu |
|---|---|---|
| Enable faillock in the stack | `authselect select <profile> <features> with-faillock` (old PAM files backed up with `--backup`; `authselect check` afterwards) | three `pam-auth-update` profiles in `/usr/share/pam-configs/linux-hardening-faillock*`, then `pam-auth-update --package` (`/etc/pam.d` copied to `/var/backups/linux-hardening-pam.d-<epoch>` first) |
| Settings | `/etc/security/faillock.conf`, rewritten as a whole: `deny=5`, `fail_interval=900`, `unlock_time=900` | same |

Root is **not** locked by default (`even_deny_root: false`): an attacker could otherwise keep root out of its own console. Extra faillock settings go in `linux_hardening_pam_faillock_extra` (`{silent: true}` writes a bare flag).

## Safety
- Remediation needs `linux_hardening_confirm_remediation: true`. `unlock_time: 0` (locked until `faillock --reset`) additionally needs `linux_hardening_pam_allow_permanent_lock: true`, and `deny` must be at least 1.
- **EL with no authselect profile selected** (hand-managed PAM files, as on a stock cloud image): the role refuses to replace them. Name a profile in `linux_hardening_pam_authselect_profile` (`minimal`, `sssd`, `winbind`) to let it select one. Roll back with `authselect backup-restore <name>` (`authselect backup-list`).
- A lockout can still hit a legitimate user who mistypes, and an attacker can lock a known account for `unlock_time`. Admins unlock with `faillock --user NAME --reset`.
- Keep a root console or a second session open when you first apply it to a remote host.

## Modes
`audit` (default) is read-only and sets `linux_hardening_pam_findings` (`key, expected, actual, fixable`). `remediate` re-audits afterwards.

## Example
```yaml
- hosts: all
  roles:
    - role: iamenr0s.linux_hardening.pam_hardening
      vars:
        linux_hardening_mode: remediate
        linux_hardening_confirm_remediation: true
        linux_hardening_pam_authselect_profile: sssd   # only used when no profile is selected yet
        linux_hardening_pam_faillock_deny: 5
```

## Verification
Container scenarios: `default`, `audit`, `refuse`, `noprofile` (EL refusal). **VM scenario `vagrant`** (libvirt; run `sg libvirt -c "molecule test -s vagrant"`, box via `MOLECULE_VAGRANT_BOX`): remediates a real VM, then attempts logins through the live stack with a small libpam helper. It proves the account locks after the configured failures (even with the right password), that `faillock --reset` unlocks it, that root is not locked, and that the SSH admin session survives. Tested: AlmaLinux 9 and Debian 13 (containers and VMs). CI runs only the container scenarios (`--exclude vagrant`).

## Rollback
EL: `authselect backup-restore`. Debian: delete the three `linux-hardening-faillock*` files in `/usr/share/pam-configs/`, run `pam-auth-update --package`, or restore `/var/backups/linux-hardening-pam.d-*`. Restore the previous `faillock.conf` from its backup.

## Known gaps
- Only lockout. No `pam_wheel`/`su` restriction, no password history, no `pam_pwquality` (see `password_policy`, not yet written).
- Not tested on Ubuntu, Fedora, EL8/10 or with an `sssd`/`winbind` profile; sssd users should check how it interacts with faillock.
- Existing local `faillock.conf` customisations are replaced (use `_extra`; the old file is backed up).
- If a hand-edited PAM stack makes `authselect select` fail, the role stops with authselect's error rather than forcing it.
- CIS IDs not mapped.

CI & Release (maintainers)
----------------------------
A single workflow (`.github/workflows/molecule.yml`) runs lint and the full Molecule distro matrix on pushes to `main`, PRs, and `v*` tags. On `v*` tags, a `release` job publishes to Ansible Galaxy after all tests pass.

One-time setup:

```bash
# Galaxy publishing key (environment-scoped, get it from galaxy.ansible.com/ui/token)
gh secret set GALAXY_API_KEY --repo iamenr0s/ansible-role-pam-hardening

# Code scanning notifications (Slack webhook URL; for Discord append /slack to the webhook URL)
gh secret set SECURITY_ALERT_WEBHOOK --repo iamenr0s/ansible-role-pam-hardening
```

`.github/workflows/code-scanning-notify.yml` polls the code-scanning API every 6 hours and posts new or updated open alerts to that webhook (GitHub Actions cannot trigger on `code_scanning_alert` directly).

To release: tag a commit `vX.Y.Z` and push the tag — CI gates the Galaxy publish.

## Contributing

Contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for the
local pipeline commands and pull request checklist. This project follows the
[Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).

## Security

See [SECURITY.md](SECURITY.md) — GitHub private vulnerability reporting, no
public issues for security bugs.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and release notes.

## License

This project is licensed under the [MIT License](LICENSE).

## Author Information

Author: iamenr0s

Galaxy: `iamenr0s.ansible_role_pam_hardening`
