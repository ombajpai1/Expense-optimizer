from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    monthly_salary = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, write_only=True)
    city_tier = serializers.IntegerField(required=False, write_only=True)
    savings_target_percentage = serializers.IntegerField(required=False, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'monthly_salary', 'city_tier', 'savings_target_percentage')

    def create(self, validated_data):
        salary = validated_data.pop('monthly_salary', 0.00)
        tier = validated_data.pop('city_tier', 2)
        savings = validated_data.pop('savings_target_percentage', 20)

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        
        # Profile is created by Signal, we just update it
        profile = user.profile
        profile.monthly_salary = salary
        profile.city_tier = tier
        profile.savings_target_percentage = savings
        profile.save()
        
        return user

class UserDetailSerializer(serializers.ModelSerializer):
    monthly_salary = serializers.DecimalField(max_digits=12, decimal_places=2, source='profile.monthly_salary')
    city_tier = serializers.IntegerField(source='profile.city_tier')
    savings_target_percentage = serializers.IntegerField(source='profile.savings_target_percentage')

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'monthly_salary', 'city_tier', 'savings_target_percentage')
        read_only_fields = ('id', 'username')

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        
        # Update User fields if any
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        # Update Profile fields
        profile = instance.profile
        profile.monthly_salary = profile_data.get('monthly_salary', profile.monthly_salary)
        profile.city_tier = profile_data.get('city_tier', profile.city_tier)
        profile.savings_target_percentage = profile_data.get('savings_target_percentage', profile.savings_target_percentage)
        profile.save()

        return instance
