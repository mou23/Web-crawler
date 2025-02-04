{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python313
    python313Packages.cbor
    python313Packages.requests
    python313Packages.beautifulsoup4
    python313Packages.numpy
    (pkgs.python313Packages.buildPythonPackage rec {
      pname = "rocksdict";
      version = "0.3.25";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/ca/c9/355ec66af66f25d5130712f18d07ef1cd677582cd106438d5b1570db0b3b/rocksdict-0.3.25-cp313-cp313-manylinux_2_28_x86_64.whl";
        sha256 = "sha256-EBCdV1U41SerfeQxZoQAO2wpZo8DhyLiesrvZAccpIE="; # Replace with actual sha256
      };
      format = "wheel";
      doCheck = false;
    })
    (pkgs.python313Packages.buildPythonPackage rec {
      pname = "spacetime";
      version = "2.1.1";
      src = ./packages/spacetime-2.1.1-py3-none-any.whl;
      format = "wheel";
      doCheck = false;
    })
    gcc
    binutils
    glibc
  ];
}
