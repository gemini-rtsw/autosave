%define _prefix /gem_base/epics/support
%define name autosave
%define repository gemdev
%define debug_package %{nil}
%define arch %(uname -m)
%define checkout %(git log --pretty=format:'%h' -n 1) 

# These defines need to be adjusted to point to the git ref
# that is to be built

# Tip 1: git remote add vendor https://github.com/epics-modules/autosave.git
# to your development sandbox to easily track both vendor/upstream and
# origin/gemini.
#
# Tip 2: git ls-remote --tags vendor to see sha and refs/tags side-by-side
#
# vendor/upstream git project
%define vendor_project https://github.com/epics-modules/autosave.git
#
# Policy:
# - prefer the latest upstream vendor tag for packaged releases
# - only follow vendor/master when we intentionally package an untagged vendor head
#
# Historical note:
# - unstable/2024q3 used vendor tag R5-10-2, mapped to package version 5.10.2
#
# Current packaged vendor baseline:
# - latest upstream vendor tag is R6-0, mapped to SemVer package version 6.0.0
%define vendor_ref R6-0

#These global defines are added to prevent stripping
# symbols on vxWorks cross-compiled code
# Getting 'strip' to work is probably only needed for
# building a related debug sub-package
#
# But this prevents all the strip warnings
# mrippa 20120202
%global _enable_debug_package 0
%global debug_package %{nil}
%global __os_install_post /usr/lib/rpm/brp-compress %{nil}

Summary: %{name} Package, a module for EPICS base
Name: %{name}
# Version corresponds to the packaged upstream vendor baseline tag.
Version: 6.0.0
Release: 0%{?dist}
License: EPICS Open License
Group: Applications/Engineering
Source0: %{name}-%{version}.tar.gz
ExclusiveArch: %{arch}
Prefix: %{_prefix}
## You may specify dependencies here
BuildRequires: epics-base-devel re2c
Requires: epics-base
## Switch dependency checking off
# AutoReqProv: no

%description
This is the module %{name}.

## If you want to have a devel-package to be generated uncomment the following:
%package devel
Summary: %{name}-devel Package
Group: Development/Gemini
Requires: %{name}
%description devel
This is the module %{name}.

%prep
%setup -q 

%build
# get vendor code
git clone --recurse-submodules %{vendor_project} vendor_project
cd vendor_project
git checkout %{vendor_ref}
git submodule update --init --recursive

# apply Gemini-specific configuration
cp ../configure/* configure/
rm -f configure/*.local

git apply ../nfsMount.patch

make distclean uninstall
make %{?_smp_mflags}

%install
# cd into the directory containing the vendor sources
cd vendor_project

export DONT_STRIP=1
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/%{_prefix}/%{name}
cp -r dbd $RPM_BUILD_ROOT/%{_prefix}/%{name}
cp -r bin $RPM_BUILD_ROOT/%{_prefix}/%{name}
cp -r lib $RPM_BUILD_ROOT/%{_prefix}/%{name}
cp -r include $RPM_BUILD_ROOT/%{_prefix}/%{name}
cp -r configure $RPM_BUILD_ROOT/%{_prefix}/%{name}
find $RPM_BUILD_ROOT/%{_prefix}/%{name}/configure -name ".git" -exec rm -rf {} \;


%postun
if [ "$1" = "0" ]; then
	rm -rf %{_prefix}/%{name}
fi


%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
   /%{_prefix}/%{name}/bin
   /%{_prefix}/%{name}/lib

%files devel
%defattr(-,root,root)
   /%{_prefix}/%{name}/dbd
   /%{_prefix}/%{name}/include
   /%{_prefix}/%{name}/configure

%changelog
