variable "DEFAULT_TAG" {
  default = "telescope-api:local"
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
    "linux/arm/v6", 
    "linux/arm/v7",
    "linux/arm64"
  ]
}

target "image-cross" {
  inherits = ["image", "docker-metadata-action"]
  platforms = [
    "linux/amd64",
    "linux/arm/v6", 
    "linux/arm/v7",
    "linux/arm64"
  ]
  cache-from = ["type=gha"]
  cache-to = ["type=gha,mode=max"]
}

target "test" {
  inherits = ["image"]
  target = "test-builder"
  platforms = ["linux/amd64"]
  output = ["type=cacheonly"]
}