using MySql.Data.MySqlClient;
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
                _logger.LogInformation("Starting database initialization...");
                
                // Get all .sql files from the Migrations folder
                var assembly = Assembly.GetExecutingAssembly();
                var resourceNames = assembly.GetManifestResourceNames()
                    .Where(name => name.EndsWith(".sql"))
                    .OrderBy(name => name) // This ensures scripts run in order (001_, 002_, etc.)
                    .ToList();

                foreach (var resourceName in resourceNames)
                {
                    _logger.LogInformation($"Running migration script: {resourceName}");
                    
                    string script;
                    using (var stream = assembly.GetManifestResourceStream(resourceName))
                    using (var reader = new StreamReader(stream))
                    {
                        script = await reader.ReadToEndAsync();
                    }

                    using (var connection = new MySqlConnection(_connectionString))
                    {
                        await connection.OpenAsync();

                        // Split the script on GO statements if present
                        // var commandStrings = script.Split(new[] { "GO" }, StringSplitOptions.RemoveEmptyEntries);
                        var commandStrings = new[] { script };
                        
                        foreach (var commandString in commandStrings)
                        {
                            if (!string.IsNullOrWhiteSpace(commandString))
                            {
                                using (var command = new MySqlCommand(commandString, connection))
                                {
                                    await command.ExecuteNonQueryAsync();
                                }
                            }
                        }
                    }
                    
                    _logger.LogInformation($"Completed migration script: {resourceName}");
                }
                
                _logger.LogInformation("Database initialization completed successfully.");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error during database initialization");
                throw;
            }
        }
    }
} 