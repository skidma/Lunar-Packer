<p align="center">
  <img src="https://cdn.discordapp.com/attachments/1186009783648649216/1481130042921848923/moon.png?ex=69b2da18&is=69b18898&hm=8a6a6569d3dbfd4ee59329186849054d0c2043dca1ac0a02134fa7d03fd34359&" width="150" alt="Lunar Logo">
</p>

<h1 align="center">Lunar Obfuscator v1.0.0</h1>

Lunar is a high-security LuaU obfuscator designed to protect scripts through a custom virtualization layer. The v1.0.0 release prioritizes execution stability and advanced stealth, providing a robust solution for protecting sensitive code in restricted environments.

> [!NOTE]
> This is my first ever major Lua and Python project. While I am actively working to make it incredible, please be aware that there are many known vulnerabilities at the moment. Use with caution as I continue to refine the security architecture.

## Technical Specifications

*   **Virtualization Logic**: Converts standard LuaU into a custom instruction set processed by a stable, table-based execution engine.
*   **Symbol Scrambling**: Renames all internal variables and function names to a non-descriptive naming cipher, removing any human-readable logic from the output.
*   **Rolling XOR Cipher**: Employs a multi-layered constant encryption system where each key is derived from the previous data block, preventing static bulk decryption.
*   **Integrity Validation**: Includes a mandatory 32-bit bytecode checksum to detect and block tampered or modified payloads.
*   **Stealth Packaging**: Automatically strips all source comments and debug logs, resulting in a compact and silent execution profile.
*   **Compatibility Optimization**: Features a flattened loader architecture to ensure reliable performance across all major Luau executors.
*   **Key Protection**: Obfuscates the session key within complex mathematical expressions to block automated extraction and analysis.

## Usage

Pack your scripts using the provided CLI tool:

```
python main.py input.lua -o output.lua
```
