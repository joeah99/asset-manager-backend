using Npgsql;
using System.Reflection;

namespace API.Services
{
    public class DatabaseInitializationService
    {
        private readonly string _connectionString;
        private readonly ILogger<DatabaseInitializationService> _logger;

        public DatabaseInitializationService(string connectionString, ILogger<DatabaseInitializationService> logger)
        {
            _connectionString = connectionString;
            _logger = logger;
        }

        public async Task InitializeAsync()
        {
            try
            {
                _logger.LogInformation("Starting PostgreSQL database initialization...");

                // Get all embedded .sql files from the Migrations folder
                var assembly = Assembly.GetExecutingAssembly();
                var resourceNames = assembly.GetManifestResourceNames()
                    .Where(name => name.EndsWith(".sql", StringComparison.OrdinalIgnoreCase))
                    .OrderBy(name => name) // Run in filename order (e.g., 001_, 002_, etc.)
                    .ToList();

                foreach (var resourceName in resourceNames)
                {
                    _logger.LogInformation($"Running migration script: {resourceName}");

                    string script;
                    using (var stream = assembly.GetManifestResourceStream(resourceName))
                    using (var reader = new StreamReader(stream!))
                    {
                        script = await reader.ReadToEndAsync();
                    }

                    // Note: PostgreSQL does not use "GO" batch separators
                    var commandStrings = new List<string> { script };

                    await using (var connection = new NpgsqlConnection(_connectionString))
                    {
                        await connection.OpenAsync();

                        foreach (var commandString in commandStrings)
                        {
                            await using (var command = new NpgsqlCommand(commandString, connection))
                            {
                                try
                                {
                                    await command.ExecuteNonQueryAsync();
                                }
                                catch (Exception innerEx)
                                {
                                    _logger.LogError(innerEx, $"Error executing script segment from {resourceName}:\n{commandString}");
                                    throw;
                                }
                            }
                        }
                    }

                    _logger.LogInformation($"Completed migration script: {resourceName}");
                }

                _logger.LogInformation("PostgreSQL database initialization completed successfully.");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error during PostgreSQL database initialization");
                throw;
            }
        }
    }
}
