# API.Tests

This project contains comprehensive unit tests for the Asset Manager Backend API.

## Test Structure

### Controllers
- `AccountControllerTests.cs` - Tests for user registration, login, password management, and preferences
- `AssetControllerTests.cs` - Tests for asset CRUD operations
- `ValuationControllerTests.cs` - Tests for asset valuation endpoints
- `LoanInformationControllerTests.cs` - Tests for loan management endpoints

### Managers
- `AccountManagerTests.cs` - Tests for account management business logic
- `AssetManagerTests.cs` - Tests for asset management business logic
- `LoanManagerTests.cs` - Tests for loan management business logic
- `ValuationManagerTests.cs` - Tests for valuation management business logic

### Services
- `AssetDepreciationServiceTests.cs` - Tests for depreciation calculation methods
- `LoanInformationServiceTests.cs` - Tests for loan calculation and schedule generation
- `AssetValuationServiceTests.cs` - Tests for asset valuation service

## Running Tests

```bash
dotnet test
```

## Test Coverage

The tests use:
- **xUnit** - Test framework
- **Moq** - Mocking framework for dependencies
- **FluentAssertions** - Readable assertion library

## Best Practices

1. Each test is isolated and independent
2. Dependencies are mocked using Moq
3. Tests follow Arrange-Act-Assert pattern
4. Test names clearly describe what is being tested

