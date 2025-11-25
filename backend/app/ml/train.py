"""
Train ML model for URL phishing detection.

This script trains a Random Forest classifier on labeled URL data
and evaluates its performance on validation and test sets.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report, confusion_matrix,
    precision_recall_fscore_support, roc_auc_score
)
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path
import logging
import argparse
import sys
import json
from datetime import datetime

from features import FeatureExtractor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_data(train_path, val_path, test_path):
    """Load train/val/test datasets."""
    logger.info("Loading datasets...")
    
    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path)
    test_df = pd.read_csv(test_path)
    
    logger.info(f"  Train: {len(train_df)} samples")
    logger.info(f"  Val:   {len(val_df)} samples")
    logger.info(f"  Test:  {len(test_df)} samples")
    
    return train_df, val_df, test_df


def extract_features_from_df(df, extractor):
    """
    Extract features from URLs in dataframe.
    
    For MVP, we only use lexical features (no enrichment data).
    """
    logger.info("Extracting features...")
    features_list = []
    failed_count = 0
    
    for idx, url in enumerate(df['url']):
        try:
            # Extract only lexical features for MVP
            # (enrichment features will be added in Phase 5)
            features = extractor.extract_all(url, enrichment_data=None)
            features_list.append(features)
        except Exception as e:
            logger.warning(f"Failed to extract features from {url}: {e}")
            # Use default features (all zeros)
            features_list.append({name: 0.0 for name in extractor.get_feature_names()})
            failed_count += 1
    
    if failed_count > 0:
        logger.warning(f"Failed to extract features from {failed_count}/{len(df)} URLs")
    
    features_df = pd.DataFrame(features_list)
    
    # Ensure all feature columns exist
    for feature_name in extractor.get_feature_names():
        if feature_name not in features_df.columns:
            features_df[feature_name] = 0.0
    
    # Reorder columns to match feature names
    features_df = features_df[extractor.get_feature_names()]
    
    logger.info(f"  Extracted {len(features_df.columns)} features")
    logger.info(f"  Feature names: {features_df.columns.tolist()[:10]}... (showing first 10)")
    
    return features_df


def train_model(X_train, y_train, model_type='random_forest'):
    """Train ML model."""
    logger.info(f"Training {model_type} model...")
    
    if model_type == 'logistic_regression':
        model = LogisticRegression(
            max_iter=1000,
            random_state=42,
            class_weight='balanced'
        )
        model.fit(X_train, y_train)
        
    elif model_type == 'random_forest':
        from sklearn.model_selection import GridSearchCV
        
        # Define parameter grid
        param_grid = {
            'n_estimators': [100, 200],
            'max_depth': [15, 20, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'class_weight': ['balanced', 'balanced_subsample']
        }
        
        rf = RandomForestClassifier(random_state=42, n_jobs=-1)
        
        logger.info("Tuning hyperparameters with GridSearchCV...")
        grid_search = GridSearchCV(
            estimator=rf,
            param_grid=param_grid,
            cv=3,
            n_jobs=-1,
            verbose=1,
            scoring='f1'
        )
        
        grid_search.fit(X_train, y_train)
        
        logger.info(f"Best parameters: {grid_search.best_params_}")
        model = grid_search.best_estimator_
        
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    logger.info("✅ Training complete!")
    
    return model


def evaluate_model(model, X, y, dataset_name='Test'):
    """Evaluate model performance."""
    logger.info(f"\nEvaluating on {dataset_name} set...")
    
    y_pred = model.predict(X)
    y_proba = model.predict_proba(X)[:, 1]  # Probability of phishing class
    
    # Calculate metrics
    precision, recall, f1, support = precision_recall_fscore_support(
        y, y_pred, average='binary', pos_label=1
    )
    
    try:
        auc = roc_auc_score(y, y_proba)
    except:
        auc = 0.0
    
    # Print results
    print(f"\n{'='*60}")
    print(f"{dataset_name} Set Results")
    print(f"{'='*60}")
    print(classification_report(y, y_pred, target_names=['Benign', 'Phishing'], digits=3))
    print(f"\nConfusion Matrix:")
    print(confusion_matrix(y, y_pred))
    print(f"\nAdditional Metrics:")
    print(f"  Precision: {precision:.3f}")
    print(f"  Recall:    {recall:.3f}")
    print(f"  F1 Score:  {f1:.3f}")
    print(f"  ROC AUC:   {auc:.3f}")
    print(f"{'='*60}\n")
    
    return {
        'precision': float(precision),
        'recall': float(recall),
        'f1': float(f1),
        'auc': float(auc),
        'support': int(support) if support is not None else 0
    }


def get_feature_importance(model, feature_names):
    """Get feature importance from trained model."""
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        feature_importance = sorted(
            zip(feature_names, importances),
            key=lambda x: x[1],
            reverse=True
        )
        
        logger.info("\nTop 10 Most Important Features:")
        for i, (feature, importance) in enumerate(feature_importance[:10], 1):
            logger.info(f"  {i:2d}. {feature:30s}: {importance:.4f}")
        
        return feature_importance
    else:
        logger.warning("Model does not support feature importance")
        return []


def save_model_artifacts(model, scaler, feature_names, metrics, model_dir, model_version):
    """Save model, scaler, and metadata."""
    logger.info(f"\nSaving model artifacts to {model_dir}...")
    
    # Save model
    model_path = model_dir / f"model_{model_version}.pkl"
    joblib.dump(model, model_path)
    logger.info(f"  ✅ Model: {model_path}")
    
    # Save scaler
    scaler_path = model_dir / f"scaler_{model_version}.pkl"
    joblib.dump(scaler, scaler_path)
    logger.info(f"  ✅ Scaler: {scaler_path}")
    
    # Save feature names
    features_path = model_dir / f"features_{model_version}.json"
    with open(features_path, 'w') as f:
        json.dump(feature_names, f, indent=2)
    logger.info(f"  ✅ Features: {features_path}")
    
    # Save metadata
    metadata = {
        'model_version': model_version,
        'model_type': type(model).__name__,
        'feature_count': len(feature_names),
        'feature_names': feature_names,
        'training_date': datetime.now().isoformat(),
        'metrics': metrics
    }
    
    metadata_path = model_dir / f"metadata_{model_version}.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"  ✅ Metadata: {metadata_path}")


def main():
    """Main training pipeline."""
    parser = argparse.ArgumentParser(description='Train URL phishing detection model')
    parser.add_argument('--model-type', type=str, default='random_forest',
                        choices=['logistic_regression', 'random_forest'],
                        help='Type of model to train')
    parser.add_argument('--model-version', type=str, default='v1.0.0',
                        help='Model version string')
    parser.add_argument('--data-dir', type=str, default=None,
                        help='Path to data directory (default: auto-detect)')
    
    args = parser.parse_args()
    
    # Determine paths
    if args.data_dir:
        data_dir = Path(args.data_dir)
    else:
        # Auto-detect: assume script is in backend/app/ml/
        script_dir = Path(__file__).parent
        data_dir = script_dir.parent.parent.parent / "data"
    
    processed_dir = data_dir / "processed"
    train_path = processed_dir / "train.csv"
    val_path = processed_dir / "val.csv"
    test_path = processed_dir / "test.csv"
    
    # Check if data exists
    if not train_path.exists():
        logger.error(f"Training data not found at {train_path}")
        logger.error("Please run data collection first: python data/scripts/collect_data.py")
        sys.exit(1)
    
    # Model directory
    model_dir = Path(__file__).parent.parent.parent.parent / "models" / "trained"
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    train_df, val_df, test_df = load_data(train_path, val_path, test_path)
    
    # Extract features
    extractor = FeatureExtractor()
    X_train = extract_features_from_df(train_df, extractor)
    X_val = extract_features_from_df(val_df, extractor)
    X_test = extract_features_from_df(test_df, extractor)
    
    y_train = train_df['label'].values
    y_val = val_df['label'].values
    y_test = test_df['label'].values
    
    # Normalize features
    logger.info("Normalizing features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    model = train_model(X_train_scaled, y_train, model_type=args.model_type)
    
    # Evaluate
    train_metrics = evaluate_model(model, X_train_scaled, y_train, 'Training')
    val_metrics = evaluate_model(model, X_val_scaled, y_val, 'Validation')
    test_metrics = evaluate_model(model, X_test_scaled, y_test, 'Test')
    
    # Feature importance
    feature_importance = get_feature_importance(model, extractor.get_feature_names())
    
    # Save artifacts
    metrics = {
        'train': train_metrics,
        'validation': val_metrics,
        'test': test_metrics
    }
    
    save_model_artifacts(
        model, scaler, extractor.get_feature_names(),
        metrics, model_dir, args.model_version
    )
    
    # Final summary
    print("\n" + "="*60)
    print("✅ Training Complete!")
    print("="*60)
    print(f"Model Type:    {args.model_type}")
    print(f"Model Version: {args.model_version}")
    print(f"Test F1 Score: {test_metrics['f1']:.3f}")
    print(f"Test Precision: {test_metrics['precision']:.3f}")
    print(f"Test Recall:   {test_metrics['recall']:.3f}")
    print("="*60)
    
    if test_metrics['f1'] < 0.85:
        print("\n⚠️  Warning: Test F1 score is below target (0.85)")
        print("   Consider:")
        print("   - Collecting more training data")
        print("   - Adding enrichment features (Phase 5)")
        print("   - Tuning hyperparameters")
    else:
        print("\n🎉 Model meets MVP target (F1 > 0.85)!")
    
    print(f"\nNext steps:")
    print(f"1. Review feature importance above")
    print(f"2. Test model: python -m app.ml.predict --url 'https://example.com'")
    print(f"3. Start backend: cd backend && uvicorn app.main:app --reload")
    print("="*60)


if __name__ == "__main__":
    main()
