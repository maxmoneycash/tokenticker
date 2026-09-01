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
      sha256 "f4e856d588f01ea68d9e7f5196cc53eedd71ac0b1ed3decafa20f62dbd2c1794"
    end
    on_intel do
      url "https://github.com/maxmoneycash/turbotokens/releases/download/v#{version}/turbotokens-macos-x64.tar.gz"
      sha256 "9c4989460010b152e70ec8709f3ca83514c58c447e57a7d45d579fc64bea8706"
    end
  end

  on_linux do
    on_intel do
      url "https://github.com/maxmoneycash/turbotokens/releases/download/v#{version}/turbotokens-linux-x64.tar.gz"
      sha256 "b67025928bd005640d087e83fddd33747200db81e204b813c5745281d06ef60a"
    end
  end

  def install
    bin.install "turbotokens"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/turbotokens --version")
  end
end
