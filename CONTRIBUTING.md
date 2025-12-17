# Contributing to Floor Plan Converter

Thank you for your interest in contributing to the Floor Plan Converter project! This document provides guidelines and instructions for contributing.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/SKETCH.git
   cd SKETCH
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Install the package in development mode**:
   ```bash
   pip install -e .
   ```

## Development Workflow

1. **Create a new branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style guidelines below

3. **Run tests** to ensure everything works:
   ```bash
   python -m unittest discover tests
   ```

4. **Test manually** with the example image:
   ```bash
   python -m floor_plan_converter IMG-20230211-WA0005.jpg -o test_output.png --verbose
   ```

5. **Commit your changes** with clear, descriptive messages:
   ```bash
   git commit -m "Add feature: description of what you added"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** on GitHub

## Code Style Guidelines

- Follow PEP 8 style guidelines for Python code
- Use meaningful variable and function names
- Add docstrings to all functions, classes, and modules
- Keep functions focused and concise
- Add comments for complex logic

### Docstring Format

Use Google-style docstrings:

```python
def example_function(param1, param2):
    """
    Brief description of the function.
    
    More detailed description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: When this exception occurs
    """
    pass
```

## Testing

- Write unit tests for new functionality
- Ensure all existing tests pass
- Test with various input images when possible
- Test edge cases and error conditions

## Areas for Contribution

Here are some areas where contributions would be particularly valuable:

### Features
- Support for curved walls and non-rectangular rooms
- Automatic scale detection from reference objects
- Support for multi-story floor plans
- Door and window detection
- Furniture detection and classification
- Integration with popular CAD software formats (DXF, DWG)
- Web interface or GUI application
- Batch processing of multiple images

### Improvements
- Better line merging algorithms
- Improved room detection accuracy
- Automatic perspective correction
- Support for colored floor plans
- Performance optimizations for large images
- Better handling of shadows and lighting variations
- Machine learning-based wall detection

### Documentation
- More usage examples
- Video tutorials
- Architecture documentation
- API documentation
- Troubleshooting guides

### Testing
- Additional unit tests
- Integration tests
- Performance benchmarks
- Test with diverse floor plan styles

## Bug Reports

When reporting bugs, please include:

1. **Description**: Clear description of the issue
2. **Steps to reproduce**: Detailed steps to reproduce the bug
3. **Expected behavior**: What you expected to happen
4. **Actual behavior**: What actually happened
5. **Environment**: Python version, OS, package versions
6. **Sample image**: If possible, include the input image that caused the issue
7. **Error messages**: Full error messages and stack traces

## Feature Requests

When requesting features:

1. **Use case**: Describe the problem you're trying to solve
2. **Proposed solution**: Your idea for how to address it
3. **Alternatives**: Other solutions you've considered
4. **Impact**: How many users would benefit from this feature

## Code Review Process

All contributions go through code review:

1. Automated tests must pass
2. Code must follow style guidelines
3. Changes must be well-documented
4. Reviewer(s) will provide feedback
5. Address feedback and update your PR
6. Once approved, changes will be merged

## Questions?

If you have questions:

- Open an issue on GitHub with the "question" label
- Check existing issues and documentation first
- Be specific about what you're trying to accomplish

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Thank You!

Thank you for contributing to making floor plan conversion more accessible and powerful!
