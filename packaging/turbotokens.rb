class Turbotokens < Formula
  desc "Real-time token and cost telemetry for AI coding agents"
  homepage "https://github.com/maxmoneycash/turbotokens"
  version "1.0.1"
  # NOTE for maintainer: on each release, update `version` and the three
  # sha256 values (shasum -a 256 on the GitHub release assets), then push to
  # the tap repo: github.com/maxmoneycash/homebrew-tap, Formula/turbotokens.rb

  on_macos do
    on_arm do
      url "https://github.com/maxmoneycash/turbotokens/releases/download/v#{version}/turbotokens-macos-arm64.tar.gz"
      sha256 "REPLACE_WITH_MACOS_ARM64_SHA256"
    end
    on_intel do
      url "https://github.com/maxmoneycash/turbotokens/releases/download/v#{version}/turbotokens-macos-x64.tar.gz"
      sha256 "REPLACE_WITH_MACOS_X64_SHA256"
    end
  end

  on_linux do
    on_intel do
      url "https://github.com/maxmoneycash/turbotokens/releases/download/v#{version}/turbotokens-linux-x64.tar.gz"
      sha256 "REPLACE_WITH_LINUX_X64_SHA256"
    end
  end

  def install
    bin.install "turbotokens"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/turbotokens --version")
  end
end
