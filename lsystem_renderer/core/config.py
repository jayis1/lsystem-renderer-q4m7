"""
Configuration management for the L-System Renderer.

Supports loading/saving configuration from YAML, JSON, and TOML files.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from .types import LSystemDefinition, LSystemRule

logger = logging.getLogger(__name__)


@dataclass
class RenderConfig:
    """Configuration for rendering output."""
    width: int = 800
    height: int = 800
    background: str = "#ffffff"
    margin: float = 20.0
    animate: bool = False
    animation_duration: float = 5.0


@dataclass
class OutputConfig:
    """Configuration for output destinations."""
    output_dir: str = "."
    filename_template: str = "{name}_{backend}"
    overwrite: bool = True


@dataclass
class LSystemConfig:
    """Comprehensive configuration for the L-System Renderer.

    Can be loaded from JSON, YAML, or TOML configuration files.
    """
    definition: Optional[LSystemDefinition] = None
    preset: Optional[str] = None
    render: RenderConfig = field(default_factory=RenderConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    seed: Optional[int] = None
    backend: str = "svg"
    iterations: Optional[int] = None

    def to_dict(self) -> dict:
        """Serialize configuration to dictionary."""
        d: Dict[str, Any] = {}
        if self.definition is not None:
            d["definition"] = self.definition.to_dict()
        if self.preset is not None:
            d["preset"] = self.preset
        if self.seed is not None:
            d["seed"] = self.seed
        d["backend"] = self.backend
        if self.iterations is not None:
            d["iterations"] = self.iterations
        d["render"] = asdict(self.render)
        d["output"] = asdict(self.output)
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "LSystemConfig":
        """Deserialize configuration from dictionary."""
        config = cls()
        if "definition" in d:
            config.definition = LSystemDefinition.from_dict(d["definition"])
        if "preset" in d:
            config.preset = d["preset"]
        if "seed" in d:
            config.seed = d["seed"]
        if "backend" in d:
            config.backend = d["backend"]
        if "iterations" in d:
            config.iterations = d["iterations"]
        if "render" in d:
            render_d = d["render"]
            config.render = RenderConfig(**{
                k: v for k, v in render_d.items()
                if k in RenderConfig.__dataclass_fields__
            })
        if "output" in d:
            output_d = d["output"]
            config.output = OutputConfig(**{
                k: v for k, v in output_d.items()
                if k in OutputConfig.__dataclass_fields__
            })
        return config

    def to_json(self, path: str) -> None:
        """Save configuration to a JSON file."""
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        logger.info("Configuration saved to %s", path)

    @classmethod
    def from_json(cls, path: str) -> "LSystemConfig":
        """Load configuration from a JSON file."""
        with open(path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def to_yaml(self, path: str) -> None:
        """Save configuration to a YAML file."""
        try:
            import yaml
        except ImportError:
            raise ImportError(
                "YAML support requires PyYAML. Install with: pip install pyyaml"
            )
        with open(path, "w") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)
        logger.info("Configuration saved to YAML: %s", path)

    @classmethod
    def from_yaml(cls, path: str) -> "LSystemConfig":
        """Load configuration from a YAML file."""
        try:
            import yaml
        except ImportError:
            raise ImportError(
                "YAML support requires PyYAML. Install with: pip install pyyaml"
            )
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data)

    def to_toml(self, path: str) -> None:
        """Save configuration to a TOML file."""
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib  # type: ignore
            except ImportError:
                raise ImportError(
                    "TOML support requires Python 3.11+ or tomli. "
                    "Install with: pip install tomli"
                )
        # For writing, we'll use a simple approach
        raise NotImplementedError(
            "TOML writing is not yet supported. Use JSON or YAML instead."
        )

    @classmethod
    def from_toml(cls, path: str) -> "LSystemConfig":
        """Load configuration from a TOML file."""
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib  # type: ignore
            except ImportError:
                raise ImportError(
                    "TOML support requires Python 3.11+ or tomli. "
                    "Install with: pip install tomli"
                )
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return cls.from_dict(data)

    @classmethod
    def from_file(cls, path: str) -> "LSystemConfig":
        """Load configuration from a file, auto-detecting format by extension.

        Supports: .json, .yaml, .yml, .toml
        """
        ext = Path(path).suffix.lower()
        if ext == ".json":
            return cls.from_json(path)
        elif ext in (".yaml", ".yml"):
            return cls.from_yaml(path)
        elif ext == ".toml":
            return cls.from_toml(path)
        else:
            raise ValueError(
                f"Unsupported config format '{ext}'. "
                f"Supported: .json, .yaml, .yml, .toml"
            )