using API.DbContext;
using API.Managers;
using API.Services;
using Microsoft.AspNetCore.Authentication.OpenIdConnect;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc.Authorization;
using Microsoft.AspNetCore.Mvc.ModelBinding.Binders;
using Quartz;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var connectionString = builder.Configuration.GetConnectionString("AZURE_SQL_CONNECTIONSTRING");
var equipmentApiKey = builder.Configuration["AppSettings:EQUIPMENT_API_KEY"];
var vehicleApiKey = builder.Configuration["AppSettings:VEHICLE_API_KEY"];
var sendGridApiKey = builder.Configuration["AppSettings:SENDGRID_API_KEY"];

// Register database initialization service
builder.Services.AddSingleton<DatabaseInitializationService>(sp =>
{
    var logger = sp.GetRequiredService<ILogger<DatabaseInitializationService>>();
    return new DatabaseInitializationService(connectionString, logger);
});

// Register other services
builder.Services.AddSingleton<AccountDbContext>(sp => new AccountDbContext(connectionString));
builder.Services.AddSingleton<AssetDbContext>(sp => new AssetDbContext(connectionString));
builder.Services.AddSingleton<AssetDepreciationScheduleDbContext>(sp => new AssetDepreciationScheduleDbContext(connectionString));
builder.Services.AddSingleton<LoanInformationDbContext>(sp => new LoanInformationDbContext(connectionString));
builder.Services.AddSingleton<LoanProjectedPaymentsDbContext>(sp => new LoanProjectedPaymentsDbContext(connectionString));
builder.Services.AddSingleton<ValuationDbContext>(sp => new ValuationDbContext(connectionString));
builder.Services.AddSingleton<DefaultDbContext>(sp => new DefaultDbContext(connectionString));

builder.Services.AddSingleton(sp => new AssetValuationService(
    new HttpClient(),
    equipmentApiKey,
    vehicleApiKey
));
builder.Services.AddScoped<ForgotPasswordService>();
builder.Services.AddSingleton(sp => new EmailService(sendGridApiKey));
builder.Services.AddSingleton(sp => new AssetDepreciationService());
builder.Services.AddSingleton<AssetManager>();
builder.Services.AddSingleton<LoanInformationService>();
builder.Services.AddSingleton<LoanManager>();
builder.Services.AddScoped<AccountManager>();
builder.Services.AddSingleton<AssetDepreciationManager>();
builder.Services.AddScoped<ValuationManager>();
builder.Services.AddQuartz(q =>
{
    q.UseMicrosoftDependencyInjectionJobFactory();
    var jobKey = new JobKey("MonthlyAssetValuationJob");
    q.AddJob<MonthlyAssetValuationJob>(opts => opts.WithIdentity(jobKey));

    q.AddTrigger(opts => opts
        .ForJob(jobKey)
        .WithIdentity("MonthlyAssetValuationJob-trigger")
        .WithCronSchedule("0 0 1 1 1/1 ? *"));  //will schedule the job to run at 1am on the first day of every month -- "0 */2 * * * ?" will run every 2 minutes for testing purposes
});
builder.Services.AddQuartzHostedService();


// Add CORS policy so the frontend can access the API
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowFrontend", policy =>
    {
        policy.WithOrigins("https://zealous-plant-0058a6510.5.azurestaticapps.net", "http://localhost:3000")
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

var app = builder.Build();

// Initialize database before starting the application
using (var scope = app.Services.CreateScope())
{
    var dbInitService = scope.ServiceProvider.GetRequiredService<DatabaseInitializationService>();
    await dbInitService.InitializeAsync();
}

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();

    app.Use(async (context, next) =>
    {
        if (context.Request.Path == "/")
        {
            context.Response.Redirect("/swagger");
            return;
        }

        await next();
    });
}

app.UseHttpsRedirection();
app.UseCors("AllowFrontend");
app.UseAuthorization();
app.MapControllers();
app.Run();
