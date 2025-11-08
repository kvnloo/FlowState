# FlowState In-Line Documentation Standards

This document defines the standard template and guidelines for in-line documentation across the FlowState codebase.

## Module Level Documentation

```python
"""Module Name and Purpose.

Detailed description of the module's functionality and purpose.

Implementation Status:
    ✓ Feature Group 1 (YYYY-MM-DD)
        - Subfeature 1
        - Subfeature 2
    ⚠ Feature Group 2 (Partial)
        - Implementation details
    ☐ Feature Group 3 (Planned)
        - Design status

Dependencies:
    - package1: Purpose/usage
    - package2: Purpose/usage

Integration Points:
    - file1.py: Integration purpose
    - file2.py: Integration purpose

Example:
    ```python
    # Basic usage example
    ```

Performance Considerations:
    - Key performance notes
    - Resource usage details

Configuration:
    Required environment variables or settings
"""
```

## Class Level Documentation

```python
class ClassName:
    """Class purpose and responsibility.

    Detailed description of the class's role and functionality.

    Attributes:
        attr1 (type): Description with valid ranges/constraints
        attr2 (type): Description with valid ranges/constraints

    Class Invariants:
        - Invariant 1
        - Invariant 2

    Example:
        ```python
        # Usage example
        ```

    Note:
        Implementation details or special considerations
    """
```

## Method Level Documentation

```python
def method_name(self, param1: type, param2: type) -> return_type:
    """Method purpose and functionality.

    Detailed description of what the method does.

    Args:
        param1: Description with valid ranges/constraints
        param2: Description with valid ranges/constraints

    Returns:
        Description of return value

    Raises:
        ExceptionType: When and why this exception occurs

    Example:
        ```python
        # Usage example
        ```

    Technical Details:
        - Implementation note 1
        - Implementation note 2

    See Also:
        related_method: Description of relationship
        OtherClass: Description of relationship
    """
```

## Documentation Guidelines

1. **Completeness**
   - All modules must have module-level docstrings
   - All classes must have class-level docstrings
   - All public methods must have method-level docstrings
   - Private methods should have docstrings if their functionality is non-trivial

2. **Implementation Status**
   - Use ✓ for completed features
   - Use ⚠ for partial implementations
   - Use ☐ for planned features
   - Include dates for completed features (YYYY-MM-DD)

3. **Dependencies**
   - List all direct dependencies
   - Explain why each dependency is needed
   - Include version constraints if specific versions are required

4. **Examples**
   - Provide clear, runnable examples
   - Include expected output where relevant
   - Show common use cases
   - Demonstrate error handling where appropriate

5. **Technical Details**
   - Document performance characteristics
   - Explain complex algorithms
   - Note any limitations or constraints
   - Include resource usage details

6. **Cross-References**
   - Link to related classes and methods
   - Reference relevant documentation
   - Point to example implementations
   - Include external resources where helpful

7. **Maintenance**
   - Update documentation when code changes
   - Keep implementation status current
   - Review and update examples regularly
   - Maintain accurate dependency information

## Style Conventions

1. **Line Length**
   - Keep docstring lines under 80 characters
   - Use proper indentation for multiline docstrings

2. **Formatting**
   - Use backticks for code references
   - Use italics for emphasis
   - Use bold for warnings or important notes
   - Use proper section headers

3. **Language**
   - Use clear, concise language
   - Write in the present tense
   - Be specific about requirements and effects
   - Avoid jargon unless necessary

4. **Type Hints**
   - Always include type hints in method signatures
   - Document complex types in docstrings
   - Explain type constraints and valid values
   - Use typing module for complex types
