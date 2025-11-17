# -----------------------------
# 1. Build Stage
# -----------------------------
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy solution and project files
COPY Asset-Manager-Backend.sln .
COPY API/API.csproj API/

# Restore dependencies
RUN dotnet restore

# Copy the rest of the API project
COPY API/ API/

# Build and publish
RUN dotnet publish API/API.csproj -c Release -o /app/publish

# -----------------------------
# 2. Runtime Stage
# -----------------------------
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app

# Copy published app from build stage
COPY --from=build /app/publish .

# Expose port 8080 (Render requires this)
EXPOSE 8080
ENV ASPNETCORE_URLS=http://+:8080

# Entry point
ENTRYPOINT ["dotnet", "API.dll"]
