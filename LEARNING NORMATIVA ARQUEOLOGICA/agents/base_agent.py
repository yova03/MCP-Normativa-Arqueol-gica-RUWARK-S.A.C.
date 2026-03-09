#!/usr/bin/env python3
"""
base_agent.py — Clase base para todos los agentes Antigravity.

Cada agente hereda de ArchaeologyAgent y define:
  - AGENT_SPEC: diccionario con nombre, dominio, fuentes, capacidades, system_prompt
  - knowledge_sources: lista de rutas .md relativas a knowledge_base/

Uso:
    from base_agent import ArchaeologyAgent
    agent = PmarAgent()
    agent.run()
"""

import os
import sys
import re
import json
import textwrap
from pathlib import Path
from datetime import datetime

# Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
KB_DIR = BASE_DIR / "knowledge_base"


class ArchaeologyAgent:
    """Agente base de consultoría arqueológica RUWARK S.A.C."""

    AGENT_SPEC = {
        "name": "Agente Base",
        "domain": "Arqueología General",
        "knowledge_sources": [],
        "capabilities": [],
        "system_prompt": "",
    }

    def __init__(self):
        self.name = self.AGENT_SPEC["name"]
        self.domain = self.AGENT_SPEC["domain"]
        self.sources = self.AGENT_SPEC["knowledge_sources"]
        self.capabilities = self.AGENT_SPEC["capabilities"]
        self.system_prompt = self.AGENT_SPEC["system_prompt"]
        self.knowledge = ""
        self.knowledge_index = {}  # {filename: content}

    # ─── KNOWLEDGE BASE ────────────────────────────────────────────

    def load_knowledge(self) -> str:
        """Lee y concatena los .md del dominio."""
        total_chars = 0
        loaded = 0
        for source in self.sources:
            path = KB_DIR / source
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.knowledge_index[source] = content
                self.knowledge += f"\n\n{'='*60}\n"
                self.knowledge += f"## FUENTE: {source}\n"
                self.knowledge += f"{'='*60}\n\n"
                self.knowledge += content
                total_chars += len(content)
                loaded += 1
            else:
                print(f"  ⚠️  No encontrado: {source}")
        
        print(f"  📚 {loaded}/{len(self.sources)} fuentes cargadas ({total_chars:,} chars)")
        return self.knowledge

    # ─── BÚSQUEDA EN KB ─────────────────────────────────────────────

    def search_knowledge(self, query: str) -> list[dict]:
        """Busca en la KB cargada y retorna fragmentos relevantes."""
        results = []
        query_lower = query.lower()
        keywords = query_lower.split()
        
        for source, content in self.knowledge_index.items():
            lines = content.split("\n")
            for i, line in enumerate(lines):
                line_lower = line.lower()
                score = sum(1 for kw in keywords if kw in line_lower)
                if score >= max(1, len(keywords) // 2):
                    # Capturar contexto (5 líneas antes y después)
                    start = max(0, i - 5)
                    end = min(len(lines), i + 6)
                    context = "\n".join(lines[start:end])
                    results.append({
                        "source": source,
                        "line": i + 1,
                        "score": score,
                        "match": line.strip(),
                        "context": context,
                    })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:10]

    # ─── ARTÍCULOS RIA ──────────────────────────────────────────────

    def get_article(self, article_num: int | str) -> str:
        """Busca un artículo específico del RIA en la KB."""
        pattern = f"Artículo {article_num}"
        for source, content in self.knowledge_index.items():
            if "ria" in source.lower():
                idx = content.find(pattern)
                if idx >= 0:
                    # Encontrar el siguiente artículo para delimitar
                    next_art = re.search(
                        r'####\s*Artículo\s+\d+',
                        content[idx + len(pattern):]
                    )
                    end = idx + len(pattern) + next_art.start() if next_art else idx + 2000
                    return content[idx:end].strip()
        return f"Artículo {article_num} no encontrado en las fuentes cargadas."

    # ─── VALIDACIÓN DE EXPEDIENTE ───────────────────────────────────

    def validate_checklist(self, checklist: dict[str, bool]) -> dict:
        """Valida un checklist de documentos y retorna resultado."""
        total = len(checklist)
        completed = sum(1 for v in checklist.values() if v)
        missing = [k for k, v in checklist.items() if not v]
        
        return {
            "total": total,
            "completed": completed,
            "missing": missing,
            "percentage": (completed / total * 100) if total > 0 else 0,
            "ready": completed == total,
        }

    # ─── INTERFAZ ───────────────────────────────────────────────────

    def print_banner(self):
        """Muestra el banner del agente."""
        width = 60
        print("\n" + "═" * width)
        print(f"  🤖 {self.name}")
        print(f"  📋 Dominio: {self.domain}")
        print("═" * width)
        print()
        print("  Capacidades:")
        for cap in self.capabilities:
            print(f"    • {cap}")
        print()
        print("─" * width)

    def print_help(self):
        """Muestra comandos disponibles."""
        commands = {
            "buscar <texto>": "Buscar en la knowledge base",
            "articulo <N>": "Ver artículo N del RIA",
            "fuentes": "Listar fuentes cargadas",
            "checklist": "Ver checklist de documentos",
            "info": "Información del agente",
            "ayuda": "Mostrar esta ayuda",
            "salir": "Salir del agente",
        }
        print("\n  Comandos disponibles:")
        for cmd, desc in commands.items():
            print(f"    {cmd:25s} {desc}")
        print()

    def handle_command(self, cmd: str) -> bool:
        """Procesa un comando. Retorna False si debe salir."""
        cmd = cmd.strip()
        
        if not cmd:
            return True
        
        if cmd.lower() in ("salir", "exit", "quit"):
            print("\n  👋 ¡Hasta luego!")
            return False
        
        if cmd.lower() in ("ayuda", "help", "?"):
            self.print_help()
            return True
        
        if cmd.lower() == "info":
            self.print_banner()
            return True
        
        if cmd.lower() == "fuentes":
            print("\n  📂 Fuentes cargadas:")
            for src in self.sources:
                status = "✅" if src in self.knowledge_index else "❌"
                size = len(self.knowledge_index.get(src, ""))
                print(f"    {status} {src} ({size:,} chars)")
            print()
            return True
        
        if cmd.lower().startswith("buscar "):
            query = cmd[7:]
            results = self.search_knowledge(query)
            if results:
                print(f"\n  🔍 {len(results)} resultados para '{query}':\n")
                for r in results[:5]:
                    print(f"  📄 {r['source']} (línea {r['line']}, score {r['score']})")
                    print(f"     {r['match'][:100]}")
                    print()
            else:
                print(f"\n  ❌ Sin resultados para '{query}'")
            return True
        
        if cmd.lower().startswith("articulo "):
            try:
                art_num = cmd.split()[1]
                text = self.get_article(art_num)
                print(f"\n{text[:2000]}")
                if len(text) > 2000:
                    print(f"\n  ... ({len(text) - 2000} chars más)")
                print()
            except (IndexError, ValueError):
                print("  Uso: articulo <número>")
            return True
        
        if cmd.lower() == "checklist":
            self.show_checklist()
            return True
        
        # Comando no reconocido: buscar en KB
        print(f"\n  ℹ️  Buscando '{cmd}' en la knowledge base...")
        results = self.search_knowledge(cmd)
        if results:
            for r in results[:3]:
                print(f"\n  📄 {r['source']} (línea {r['line']}):")
                for line in r['context'].split('\n'):
                    print(f"     {line}")
        else:
            print(f"  Sin resultados. Usa 'ayuda' para ver comandos disponibles.")
        print()
        return True

    def show_checklist(self):
        """Override en cada agente para mostrar su checklist."""
        print("  Este agente no tiene checklist definido.")

    # ─── EJECUCIÓN ──────────────────────────────────────────────────

    def run(self):
        """Loop principal del agente."""
        self.print_banner()
        print("  Cargando knowledge base...")
        self.load_knowledge()
        print()
        print("  Escribe tu consulta, comando, o 'ayuda':")
        print()
        
        while True:
            try:
                query = input("  >> ")
                if not self.handle_command(query):
                    break
            except (KeyboardInterrupt, EOFError):
                print("\n\n  👋 ¡Hasta luego!")
                break
