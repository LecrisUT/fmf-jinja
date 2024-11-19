Name:           fmf-jinja
Version:        0.0.0
Release:        %autorelease
Summary:        Jinja template engine using FMF metadata

License:        GPL-3.0-or-later
URL:            https://github.com/LecrisUT/fmf-jinja
Source:         %{pypi_source tmt_cmake}

BuildArch:      noarch
BuildRequires:  python3-devel

%py_provides python3-fmf-jinja

%description
Jinja template engine using FMF metadata


%prep
%autosetup -n fmf-jinja-%{version}


%generate_buildrequires
%pyproject_buildrequires -x test


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files fmf_jinja


%check
%pytest


%files -f %{pyproject_files}
%{_bindir}/fmf-jinja
%license LICENSE.md
%doc README.md


%changelog
%autochangelog
