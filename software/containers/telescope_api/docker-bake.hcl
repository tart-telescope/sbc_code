variable "DEFAULT_TAG" {
  default = "telescope-api:local"
}

variable "GIT_COMMIT" {
  default = "unknown"
}

# https://github.com/docker/metadata-action#bake-definition
target "docker-metadata-action" {}

# Default target
group "default" {
  targets = ["image-local"]
}

# All targets
group "all" {
  targets = ["image-all"]
}

target "image" {
  context = "."
  dockerfile = "Dockerfile"
  args = {
    GIT_COMMIT = "${GIT_COMMIT}"
  }
}

target "image-local" {
  inherits = ["image"]
  tags = ["${DEFAULT_TAG}"]
  platforms = ["linux/amd64"]
}

target "image-all" {
  inherits = ["image"]
  tags = ["${DEFAULT_TAG}"]
  platforms = [
    "linux/amd64",
    "linux/arm/v7",
    "linux/arm64"
  ]
}

target "image-cross" {
  inherits = ["image", "docker-metadata-action"]
  platforms = [
    "linux/amd64",
    "linux/arm/v7",
    "linux/arm64"
  ]
  cache-from = ["type=gha"]
  cache-to = ["type=gha,mode=max"]
}

# Single-platform arm64 build loaded into the local daemon for the pre-publish
# smoke test (issue #25): runs the image under QEMU and exercises the runtime
# (stdlib + pydantic/fastapi imports, forced GC) before anything is pushed.
target "image-smoke" {
  inherits = ["image"]
  tags = ["telescope-api:smoke"]
  platforms = ["linux/arm64"]
  output = ["type=docker"]
  cache-from = ["type=gha"]
  cache-to = ["type=gha,mode=max"]
}

target "test" {
  inherits = ["image"]
  target = "test-builder"
  platforms = ["linux/amd64"]
  output = ["type=cacheonly"]
}
