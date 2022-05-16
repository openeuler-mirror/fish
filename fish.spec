Name:           fish
Version:        3.3.1
Release:        4
Summary:        Friendly interactive shell
License:        GPLv2 and BSD and ISC and LGPLv2+ and MIT
URL:            https://fishshell.com
Source0:        https://github.com/fish-shell/fish-shell/releases/download/%{version}/%{name}-%{version}.tar.xz
# https://github.com/fish-shell/fish-shell/commit/ec8844d834cc9fe626e9fc326c6f5410341d532a
Patch01:        fix-test-failure.patch
# https://github.com/fish-shell/fish-shell/commit/37625053d424c1ab88de2b0c50c7fe71e1468e2c
Patch02:        CVE-2022-20001.patch

BuildRequires:  cmake >= 3.2
BuildRequires:  ninja-build
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  gettext
BuildRequires:  ncurses-devel
BuildRequires:  pcre2-devel
BuildRequires:  gnupg2
BuildRequires:  python3-devel
%global __python %{__python3}
BuildRequires:  /usr/bin/desktop-file-validate

# tab completion wants man-db
Recommends:     man-db
Recommends:     man-pages
Recommends:     groff-base

Provides:       bundled(js-angular) = 1.0.8
Provides:       bundled(js-jquery) = 3.3.1
Provides:       bundled(js-underscore) = 1.9.1

%description
fish is a fully-equipped command line shell (like bash or zsh) that is
smart and user-friendly. fish supports powerful features like syntax
highlighting, autosuggestions, and tab completions that just work, with
nothing to learn or configure.

%prep
%autosetup -p1
rm -vrf pcre2-*

# Change the bundled scripts to invoke the python binary directly.
for f in $(find share/tools -type f -name '*.py'); do
    sed -i -e '1{s@^#!.*@#!%{__python3}@}' "$f"
done

%build
%cmake . -B%{_vpath_builddir} -GNinja \
    -DCMAKE_INSTALL_SYSCONFDIR=%{_sysconfdir} \
    -Dextra_completionsdir=%{_datadir}/%{name}/vendor_completions.d \
    -Dextra_functionsdir=%{_datadir}/%{name}/vendor_functions.d \
    -Dextra_confdir=%{_datadir}/%{name}/vendor_conf.d

%ninja_build -C %{_vpath_builddir} all fish_tests

sed -i 's^/usr/local/^/usr/^g' %{_vpath_builddir}/*.pc

%install
%ninja_install -C %{_vpath_builddir}

%py_byte_compile %{__python3} %{buildroot}%{_datadir}/%{name}/tools/

# Install docs from tarball root
cp -a README.rst %{buildroot}%{_pkgdocdir}
cp -a CONTRIBUTING.rst %{buildroot}%{_pkgdocdir}

%find_lang %{name}

%check
%{_vpath_builddir}/fish_tests
desktop-file-validate %{buildroot}%{_datadir}/applications/fish.desktop

%post
if [ "$1" = 1 ]; then
  if [ ! -f %{_sysconfdir}/shells ] ; then
    echo "%{_bindir}/fish" > %{_sysconfdir}/shells
    echo "/bin/fish" >> %{_sysconfdir}/shells
  else
    grep -q "^%{_bindir}/fish$" %{_sysconfdir}/shells || echo "%{_bindir}/fish" >> %{_sysconfdir}/shells
    grep -q "^/bin/fish$" %{_sysconfdir}/shells || echo "/bin/fish" >> %{_sysconfdir}/shells
  fi
fi

%postun
if [ "$1" = 0 ] && [ -f %{_sysconfdir}/shells ] ; then
  sed -i '\!^%{_bindir}/fish$!d' %{_sysconfdir}/shells
  sed -i '\!^/bin/fish$!d' %{_sysconfdir}/shells
fi

%files -f %{name}.lang
%license COPYING
%{_mandir}/man1/fish*.1*
%{_bindir}/fish*
%config(noreplace) %{_sysconfdir}/fish/
%{_datadir}/fish/
%{_datadir}/pkgconfig/fish.pc
%{_pkgdocdir}
%{_datadir}/applications/fish.desktop
%{_datadir}/pixmaps/fish.png

%changelog
* Mon May 16 2022 yaoxin <yaoxin30@h-partners.com> - 3.3.1-4
- Fix CVE-2022-20001

* Fri Mar 11 2022 wulei <wulei80@huawei.com> - 3.3.1-3
- Add comment: https://github.com/fish-shell/fish-shell/commit/ec8844d834cc9fe626e9fc326c6f5410341d532a

* Thu Mar 10 2022 wulei <wulei80@huawei.com> - 3.3.1-2
- Fix test failure

* Mon July 12 2021 wulei <wulei80@huawei.com> - 3.3.1-1
- Package init
