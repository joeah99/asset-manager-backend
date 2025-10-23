using System;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;
using API.DTOs;

namespace API.Services
{
    public class AssetValuationService
    {
        private readonly HttpClient _httpClient;
        private readonly string _equipmentApiKey;
        private readonly string _vehicleApiKey;
        private const string EquipmentWatchTaxonomyUrl = "https://equipmentwatchapi.com/v1/taxonomy/models";
        private const string EquipmentWatchValueUrl = "https://equipmentwatchapi.com/v1/values/value";
        private const string PriceDigestTaxonomyUrl = "https://pricedigestsapi.com/v1/taxonomy/configurations/";
        private const string PriceDigestValueUrl = "https://pricedigestsapi.com/v1/values/value/";

        public AssetValuationService(HttpClient httpClient, string equipmentApiKey, string vehicleApiKey)
        {
            _httpClient = httpClient;
            _equipmentApiKey = equipmentApiKey;
            _vehicleApiKey = vehicleApiKey;
        }

        private string BuildTaxonomyApiUrl(string baseUrl, string manufacturer, string model, string modelYear)
        {
            return $"{baseUrl}?model={Uri.EscapeDataString(model)}&manufacturer={Uri.EscapeDataString(manufacturer)}&modelYear={Uri.EscapeDataString(modelYear)}";
        }

        private string BuildValueApiUrl(string baseUrl, string modelId, string year, string usage, string condition, string country, string region)
        {
            return $"{baseUrl}?modelId={Uri.EscapeDataString(modelId)}&year={year}&usage={usage}&condition={Uri.EscapeDataString(condition)}&country={Uri.EscapeDataString(country)}&region={Uri.EscapeDataString(region)}";
        }

        private string BuildVehicleValueApiUrl(string baseUrl, string configurationId, string usage, string condition, string country, string state)
        {
            return $"{baseUrl}?configurationId={Uri.EscapeDataString(configurationId)}&usage={usage}&condition={Uri.EscapeDataString(condition)}&country={Uri.EscapeDataString(country)}&state={Uri.EscapeDataString(state)}";
        }

        private string GetApiKey(string assetType)
        {
            return assetType == "Equipment" ? _equipmentApiKey : _vehicleApiKey;
        }

        public async Task<EquipmentValuationDTO> GetEquipmentValuationAsync(string manufacturer, string model, string modelYear, string usage, string condition, string country, string region)
{
    var taxonomyApiUrl = BuildTaxonomyApiUrl(EquipmentWatchTaxonomyUrl, manufacturer, model, modelYear);
    var apiKey = GetApiKey("Equipment");

    var taxonomyRequest = new HttpRequestMessage(HttpMethod.Get, taxonomyApiUrl);
    taxonomyRequest.Headers.Add("x-api-key", apiKey);

    var taxonomyResponse = await _httpClient.SendAsync(taxonomyRequest);

    if (!taxonomyResponse.IsSuccessStatusCode)
    {
        throw new HttpRequestException($"Error fetching Equipment taxonomy. Status Code: {taxonomyResponse.StatusCode}");
    }

    using var taxonomyStream = await taxonomyResponse.Content.ReadAsStreamAsync();
    var taxonomyData = await JsonSerializer.DeserializeAsync<JsonElement>(taxonomyStream);

    string modelId = null;

    if (taxonomyData.ValueKind == JsonValueKind.Object)
    {
        if (taxonomyData.TryGetProperty("modelId", out JsonElement modelIdElement))
        {
            modelId = modelIdElement.GetString();
        }
    }
    else if (taxonomyData.ValueKind == JsonValueKind.Array)
    {
        foreach (var element in taxonomyData.EnumerateArray())
        {
            if (element.TryGetProperty("modelId", out JsonElement modelIdElement))
            {
                modelId = modelIdElement.GetInt32().ToString();
                break;
            }
        }
    }

    if (string.IsNullOrEmpty(modelId))
    {
        throw new InvalidOperationException("No valid model ID found in taxonomy data.");
    }

    // Fetch valuation data
    var valuationApiUrl = BuildValueApiUrl(EquipmentWatchValueUrl, modelId, modelYear, usage, condition, country, region);
    var valuationRequest = new HttpRequestMessage(HttpMethod.Get, valuationApiUrl);
    valuationRequest.Headers.Add("x-api-key", apiKey);

    var valuationResponse = await _httpClient.SendAsync(valuationRequest);

    if (!valuationResponse.IsSuccessStatusCode)
    {
        throw new HttpRequestException($"Error fetching Equipment valuation. Status Code: {valuationResponse.StatusCode}");
    }

    using var valuationStream = await valuationResponse.Content.ReadAsStreamAsync();
    var valuationData = await JsonSerializer.DeserializeAsync<EquipmentValuationDTO>(valuationStream);

    return valuationData;
}

public async Task<VehicleValuationDTO> GetVehicleValuationAsync(string manufacturer, string model, string modelYear, string usage, string condition, string country, string region)
{
    var taxonomyApiUrl = BuildTaxonomyApiUrl(PriceDigestTaxonomyUrl, manufacturer, model, modelYear);
    var apiKey = GetApiKey("Vehicle");

    var taxonomyRequest = new HttpRequestMessage(HttpMethod.Get, taxonomyApiUrl);
    taxonomyRequest.Headers.Add("x-api-key", apiKey);

    var taxonomyResponse = await _httpClient.SendAsync(taxonomyRequest);

    if (!taxonomyResponse.IsSuccessStatusCode)
    {
        throw new HttpRequestException($"Error fetching Vehicle taxonomy. Status Code: {taxonomyResponse.StatusCode}");
    }

    using var taxonomyStream = await taxonomyResponse.Content.ReadAsStreamAsync();
    var taxonomyData = await JsonSerializer.DeserializeAsync<JsonElement>(taxonomyStream);

    string configurationId = null;

    // Handle taxonomy data as an array
    if (taxonomyData.ValueKind == JsonValueKind.Array)
    {
        foreach (var item in taxonomyData.EnumerateArray())
        {
            if (item.TryGetProperty("configurationId", out var configurationIdProperty))
            {
                configurationId = configurationIdProperty.GetInt32().ToString();
                if (!string.IsNullOrEmpty(configurationId))
                {
                    break; 
                }
            }
        }
    }

    if (string.IsNullOrEmpty(configurationId))
    {
        throw new InvalidOperationException("No valid configuration ID found in taxonomy data.");
    }

    // Fetch valuation data
    var valuationApiUrl = BuildVehicleValueApiUrl(PriceDigestValueUrl, configurationId, usage, condition, country, region);
    var valuationRequest = new HttpRequestMessage(HttpMethod.Get, valuationApiUrl);
    valuationRequest.Headers.Add("x-api-key", apiKey);

    var valuationResponse = await _httpClient.SendAsync(valuationRequest);

    if (!valuationResponse.IsSuccessStatusCode)
    {
        throw new HttpRequestException($"Error fetching Vehicle valuation. Status Code: {valuationResponse.StatusCode}");
    }

    using var valuationStream = await valuationResponse.Content.ReadAsStreamAsync();
    return await JsonSerializer.DeserializeAsync<VehicleValuationDTO>(valuationStream);
}

    }
}
